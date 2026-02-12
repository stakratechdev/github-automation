"""
Requirements Engineer Agent.
Monitors and analyzes GitHub issues for requirements clarification.
"""

import logging
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from common.config_loader import AgentConfig, get_config
from common.github_client import GitHubClient, GitHubIssue
from common.mqtt_client import MQTTClient
from common.llm_client import LLMClient
from common.event_types import (
    EventType,
    IssueStatus,
    AgentEvent,
    create_event,
    StatusManager
)

logger = logging.getLogger(__name__)


class RequirementsEngineerAgent:
    """
    Requirements Engineer Agent.
    
    Responsibilities:
    - Monitor new/updated GitHub issues
    - Analyze requirements semantically
    - Generate clarification questions
    - Set issues to "ready for implementation"
    - Trigger next agents via events
    """
    
    def __init__(
        self,
        agent_config: Optional[AgentConfig] = None,
        github_client: Optional[GitHubClient] = None,
        mqtt_client: Optional[MQTTClient] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """Initialize the Requirements Engineer Agent."""
        self.config = agent_config or get_config().agents.get(
            'requirements_engineer',
            AgentConfig(name="requirements-engineer")
        )
        
        self.github = github_client or GitHubClient()
        self.mqtt = mqtt_client or MQTTClient()
        self.llm = llm_client or LLMClient()
        
        self.name = self.config.name
        self.running = False
        self._stop_event = threading.Event()
        self._last_poll: Optional[datetime] = None
        
        # Track issues being clarified
        self._clarification_issues: Dict[int, Dict] = {}
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def start(self) -> None:
        """Start the agent."""
        logger.info(f"Starting {self.name} agent...")
        
        # Connect to MQTT
        self.mqtt.connect()
        
        # Publish agent started event
        self.mqtt.publish(create_event(
            EventType.AGENT_STARTED,
            self.name,
            payload={"agent_type": "requirements_engineer"}
        ))
        
        self.running = True
        self._stop_event.clear()
        
        # Start polling loop
        self._polling_thread = threading.Thread(target=self._poll_loop)
        self._polling_thread.daemon = True
        self._polling_thread.start()
        
        logger.info(f"{self.name} agent started successfully")
    
    def stop(self) -> None:
        """Stop the agent."""
        logger.info(f"Stopping {self.name} agent...")
        
        self.running = False
        self._stop_event.set()
        
        # Publish agent stopped event
        self.mqtt.publish(create_event(
            EventType.AGENT_STOPPED,
            self.name,
            payload={"agent_type": "requirements_engineer"}
        ))
        
        self.mqtt.disconnect()
        
        logger.info(f"{self.name} agent stopped")
    
    def _poll_loop(self) -> None:
        """Main polling loop."""
        while self.running and not self._stop_event.is_set():
            try:
                self._process_issues()
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                self.mqtt.publish(create_event(
                    EventType.AGENT_ERROR,
                    self.name,
                    payload={"error": str(e)}
                ))
            
            # Wait for poll interval
            self._stop_event.wait(self.config.poll_interval)
    
    def _process_issues(self) -> None:
        """Process issues in the monitoring state."""
        new_label = self.config.labels.new
        blocked_label = self.config.labels.blocked
        ready_label = self.config.labels.ready
        
        # Get issues that need analysis
        issues = self.github.get_issues(state="open", labels=[new_label])
        
        for issue in issues:
            if self._stop_event.is_set():
                break
            
            try:
                self._analyze_issue(issue)
            except Exception as e:
                logger.error(f"Error analyzing issue #{issue.number}: {e}")
    
    def _analyze_issue(self, issue: GitHubIssue) -> None:
        """Analyze a single issue for requirements clarity."""
        logger.info(f"Analyzing issue #{issue.number}: {issue.title}")
        
        # Publish analysis started event
        self.mqtt.publish(create_event(
            EventType.ISSUE_UPDATED,
            self.name,
            issue.number,
            payload={"action": "analysis_started", "title": issue.title}
        ))
        
        # Check for existing clarification comments
        comments = self.github.get_comments(issue.number)
        clarification_count = sum(
            1 for c in comments if c.user != self.name
        )
        
        if clarification_count == 0:
            # First time seeing this issue - analyze requirements
            self._analyze_and_ask(issue)
        else:
            # Check if user has responded to clarifications
            self._check_responses(issue, comments)
    
    def _analyze_and_ask(self, issue: GitHubIssue) -> None:
        """Analyze requirements and generate clarification questions."""
        # Analyze the requirement using LLM
        analysis = self.llm.analyze_requirement(issue.body)
        
        # Generate clarification questions
        questions = self.llm.generate_clarification_questions(issue.body)
        
        # Check if clarification is needed
        needs_clarification = (
            analysis.get('needs_clarification', False) or
            len(questions) > 0
        )
        
        if needs_clarification:
            # Post clarification questions
            self._post_clarification_questions(issue, questions, analysis)
            
            # Set status to waiting_for_clarification
            self.github.set_status_label(
                issue.number,
                IssueStatus.WAITING_FOR_CLARIFICATION
            )
            
            # Track this issue
            self._clarification_issues[issue.number] = {
                'questions_asked': questions,
                'analysis': analysis,
                'asked_at': datetime.utcnow()
            }
            
            # Publish event
            self.mqtt.publish(create_event(
                EventType.STATUS_CHANGED,
                self.name,
                issue.number,
                payload={
                    "action": "waiting_for_clarification",
                    "questions_count": len(questions)
                }
            ))
            
        else:
            # Requirements are clear - mark as ready for dev
            self._mark_ready_for_dev(issue, analysis)
    
    def _post_clarification_questions(
        self,
        issue: GitHubIssue,
        questions: List[str],
        analysis: Dict
    ) -> None:
        """Post clarification questions as a comment."""
        # Format the comment
        comment = self._format_clarification_comment(questions, analysis)
        
        # Add comment
        self.github.add_comment(issue.number, comment)
        
        logger.info(f"Posted {len(questions)} clarification questions for issue #{issue.number}")
    
    def _format_clarification_comment(
        self,
        questions: List[str],
        analysis: Dict
    ) -> str:
        """Format a clarification comment."""
        lines = [
            "## 🔍 Requirements Analysis",
            "",
            "Ich habe Ihre Anforderung analysiert und benötige einige Präzisierungen:",
            ""
        ]
        
        # Add questions
        lines.append("### ❓ Klärungsfragen:")
        for i, q in enumerate(questions, 1):
            lines.append(f"{i}. {q}")
        
        lines.append("")
        
        # Add analysis summary if available
        if 'functional_requirements' in analysis:
            lines.append("### 📋 Erkannte Funktionale Anforderungen:")
            for req in analysis.get('functional_requirements', []):
                lines.append(f"- {req}")
            lines.append("")
        
        if 'dependencies' in analysis:
            lines.append("### 🔗 Erkannte Abhängigkeiten:")
            for dep in analysis.get('dependencies', []):
                lines.append(f"- {dep}")
            lines.append("")
        
        lines.append("---")
        lines.append("*Bitte beantworten Sie diese Fragen, damit ich die Anforderung vollständig verstehen und mit der Implementierung beginnen kann.*")
        lines.append("")
        lines.append("*Requirements Engineer Agent*")
        
        return "\n".join(lines)
    
    def _check_responses(self, issue: GitHubIssue, comments: List) -> None:
        """Check if user has responded to clarification questions."""
        if issue.number not in self._clarification_issues:
            return
        
        tracking = self._clarification_issues[issue.number]
        
        # Get new comments since we asked
        asked_at = tracking['asked_at']
        new_comments = [
            c for c in comments
            if c.user != self.name and
            datetime.fromisoformat(c.created_at.replace('Z', '+00:00')) > asked_at
        ]
        
        if len(new_comments) > 0:
            # User has responded - analyze and mark ready
            logger.info(f"User responded to issue #{issue.number}, analyzing response...")
            
            # Analyze all comments for sufficient information
            all_responses = " ".join([c.body for c in new_comments])
            analysis = self.llm.analyze_requirement(
                issue.body + "\n\nUser Clarifications:\n" + all_responses
            )
            
            # Check if requirements are now clear
            needs_more = (
                analysis.get('needs_clarification', False) or
                "?" in all_responses
            )
            
            if not needs_more:
                self._mark_ready_for_dev(issue, analysis)
                del self._clarification_issues[issue.number]
            else:
                # Ask follow-up questions
                follow_up = self.llm.generate_clarification_questions(
                    issue.body + "\n\nUser Clarifications:\n" + all_responses
                )
                self._post_clarification_questions(issue, follow_up, analysis)
                tracking['asked_at'] = datetime.utcnow()
    
    def _mark_ready_for_dev(self, issue: GitHubIssue, analysis: Dict) -> None:
        """Mark issue as ready for development."""
        # Update issue with analysis summary
        analysis_text = self._format_analysis_summary(analysis)
        
        updated_body = f"""**Anforderungsanalyse:**

{analysis_text}

---

*Original issue:*"""

        self.github.update_issue(
            issue.number,
            body=updated_body + issue.body
        )
        
        # Update labels
        self.github.set_status_label(issue.number, IssueStatus.READY_FOR_DEV)
        
        # Add ready_for_dev label if different
        ready_label = self.config.labels.ready
        if ready_label:
            self.github.add_labels(issue.number, [ready_label])
        
        # Publish event to trigger next agents
        self.mqtt.publish(create_event(
            EventType.STATUS_CHANGED,
            self.name,
            issue.number,
            payload={
                "action": "ready_for_dev",
                "analysis_summary": analysis.get('raw_analysis', '')[:500],
                "suggested_approach": analysis.get('suggested_implementation_approach', '')
            }
        ))
        
        logger.info(f"Issue #{issue.number} marked as ready for development")
    
    def _format_analysis_summary(self, analysis: Dict) -> str:
        """Format analysis summary for the issue."""
        lines = []
        
        if 'functional_requirements' in analysis:
            lines.append("**Funktionale Anforderungen:**")
            for req in analysis.get('functional_requirements', []):
                lines.append(f"- {req}")
            lines.append("")
        
        if 'suggested_implementation_approach' in analysis:
            lines.append("**Empfohlener Implementierungsansatz:**")
            lines.append(analysis['suggested_implementation_approach'])
            lines.append("")
        
        if 'dependencies' in analysis:
            lines.append("**Abhängigkeiten:**")
            for dep in analysis.get('dependencies', []):
                lines.append(f"- {dep}")
            lines.append("")
        
        if 'potential_risks' in analysis:
            lines.append("**Potenzielle Risiken:**")
            for risk in analysis.get('potential_risks', []):
                lines.append(f"- {risk}")
            lines.append("")
        
        return "\n".join(lines)
    
    def process_webhook(self, payload: Dict) -> None:
        """
        Process GitHub webhook event.
        
        Args:
            payload: Webhook payload
        """
        action = payload.get('action')
        issue = payload.get('issue')
        
        if not issue:
            return
        
        issue_number = issue['number']
        
        if action in ['opened', 'reopened']:
            # New or reopened issue - process it
            github_issue = GitHubIssue.from_api(issue)
            self._analyze_issue(github_issue)
        
        elif action == 'created' and 'comment' in payload:
            # New comment - check if it's a user response
            github_issue = GitHubIssue.from_api(issue)
            comments = self.github.get_comments(issue_number)
            self._check_responses(github_issue, comments)


def main():
    """Main entry point for the agent."""
    agent = RequirementsEngineerAgent()
    
    try:
        agent.start()
        
        # Keep main thread alive
        while agent.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    main()
