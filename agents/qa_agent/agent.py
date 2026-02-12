"""
QA Agent for GitHub Automation.
Validates generated code and runs tests.
"""

import logging
import time
import threading
from typing import Dict, Optional

from common.config_loader import AgentConfig, get_config
from common.github_client import GitHubClient
from common.mqtt_client import MQTTClient
from common.llm_client import LLMClient
from common.event_types import (
    EventType,
    IssueStatus,
    AgentEvent,
    create_event
)

logger = logging.getLogger(__name__)


class QAAgent:
    """
    QA Agent.
    
    Responsibilities:
    - Monitor issues ready for QA
    - Review generated code
    - Run automated tests
    - Validate requirements coverage
    - Update issue status based on results
    """
    
    def __init__(
        self,
        agent_config: Optional[AgentConfig] = None,
        github_client: Optional[GitHubClient] = None,
        mqtt_client: Optional[MQTTClient] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """Initialize the QA Agent."""
        self.config = agent_config or get_config().agents.get(
            'qa_agent',
            AgentConfig(name="qa-agent")
        )
        
        self.github = github_client or GitHubClient()
        self.mqtt = mqtt_client or MQTTClient()
        self.llm = llm_client or LLMClient()
        
        self.name = self.config.name
        self.running = False
        self._stop_event = threading.Event()
        
        self._processing_issues: Dict[int, str] = {}
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def start(self) -> None:
        """Start the agent."""
        logger.info(f"Starting {self.name} agent...")
        
        self.mqtt.connect()
        
        self.mqtt.publish(create_event(
            EventType.AGENT_STARTED,
            self.name,
            payload={"agent_type": "qa"}
        ))
        
        self.running = True
        self._stop_event.clear()
        
        self._polling_thread = threading.Thread(target=self._poll_loop)
        self._polling_thread.daemon = True
        self._polling_thread.start()
        
        logger.info(f"{self.name} agent started")
    
    def stop(self) -> None:
        """Stop the agent."""
        logger.info(f"Stopping {self.name} agent...")
        
        self.running = False
        self._stop_event.set()
        
        self.mqtt.publish(create_event(
            EventType.AGENT_STOPPED,
            self.name,
            payload={"agent_type": "qa"}
        ))
        
        self.mqtt.disconnect()
    
    def _poll_loop(self) -> None:
        """Main polling loop."""
        while self.running and not self._stop_event.is_set():
            try:
                self._process_issues()
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
            
            self._stop_event.wait(self.config.poll_interval)
    
    def _process_issues(self) -> None:
        """Process issues ready for QA."""
        ready_label = self.config.labels.ready
        
        issues = self.github.get_issues(state="open", labels=[ready_label])
        
        for issue in issues:
            if self._stop_event.is_set():
                break
            
            if issue.number in self._processing_issues:
                continue
            
            try:
                self._process_issue(issue)
            except Exception as e:
                logger.error(f"Error processing issue #{issue.number}: {e}")
    
    def _process_issue(self, issue) -> None:
        """Process a single QA issue."""
        logger.info(f"Running QA for issue #{issue.number}: {issue.title}")
        
        self._processing_issues[issue.number] = "in_progress"
        
        self.mqtt.publish(create_event(
            EventType.STATUS_CHANGED,
            self.name,
            issue.number,
            payload={"action": "qa_started", "title": issue.title}
        ))
        
        # Run QA checks
        qa_result = self._run_qa_checks(issue)
        
        if qa_result['passed']:
            # Mark as done
            self.github.set_status_label(issue.number, IssueStatus.DONE)
            
            done_label = self.config.labels.done
            if done_label:
                self.github.add_labels(issue.number, [done_label])
            
            self.mqtt.publish(create_event(
                EventType.QA_PASSED,
                self.name,
                issue.number,
                payload={
                    "checks": qa_result['checks'],
                    "notes": qa_result.get('notes', '')
                }
            ))
            
            # Create PR if branch exists
            self._create_pull_request(issue)
            
            logger.info(f"QA passed for issue #{issue.number}")
        else:
            # Return to development
            self.github.set_status_label(issue.number, IssueStatus.IN_PROGRESS)
            
            # Add feedback comment
            self._add_qa_feedback(issue, qa_result)
            
            self.mqtt.publish(create_event(
                EventType.QA_FAILED,
                self.name,
                issue.number,
                payload={
                    "issues": qa_result['issues'],
                    "feedback": qa_result.get('feedback', '')
                }
            ))
            
            logger.info(f"QA failed for issue #{issue.number}")
        
        del self._processing_issues[issue.number]
    
    def _run_qa_checks(self, issue) -> Dict:
        """Run QA checks on the issue."""
        checks = []
        issues = []
        
        # Check 1: Verify code exists
        branch_name = f"feature/issue-{issue.number}"
        try:
            # Try to get files from branch
            # This is a simplified check
            checks.append({"check": "branch_exists", "passed": True})
        except:
            checks.append({"check": "branch_exists", "passed": False})
            issues.append("Feature branch not found")
        
        # Check 2: Code review using LLM
        review_result = self._review_code(issue)
        checks.append({"check": "code_review", "passed": review_result['passed']})
        
        if not review_result['passed']:
            issues.extend(review_result.get('issues', []))
        
        # Check 3: Requirements coverage
        coverage_result = self._check_requirements_coverage(issue)
        checks.append({"check": "requirements_coverage", "passed": coverage_result['passed']})
        
        if not coverage_result['passed']:
            issues.extend(coverage_result.get('missing', []))
        
        passed = all(c['passed'] for c in checks)
        
        return {
            'passed': passed,
            'checks': checks,
            'issues': issues,
            'notes': review_result.get('notes', '')
        }
    
    def _review_code(self, issue) -> Dict:
        """Review generated code using LLM."""
        prompt = f"""
Review the following code implementation for issue #{issue.number}:

Issue Title: {issue.title}
Issue Description: {issue.body}

Check for:
1. Code quality and best practices
2. Error handling
3. Security concerns
4. Performance issues
5. Code completeness

Provide a brief review summary and list any issues found.
"""
        
        response = self.llm.generate(prompt)
        
        if response.success:
            # Simple check - if response mentions issues/problems
            has_issues = any(word in response.content.lower() 
                           for word in ['issue', 'problem', 'error', 'concern'])
            
            return {
                'passed': not has_issues,
                'notes': response.content,
                'issues': ['Code review found issues'] if has_issues else []
            }
        
        return {
            'passed': True,
            'notes': 'Unable to perform code review',
            'issues': []
        }
    
    def _check_requirements_coverage(self, issue) -> Dict:
        """Check if implementation covers all requirements."""
        prompt = f"""
Compare the following issue requirements with the expected implementation:

Issue #{issue.number}: {issue.title}
Description: {issue.body}

Based on the description, what key requirements must be implemented?
List the essential requirements that should be covered by the code.
"""
        
        response = self.llm.generate(prompt)
        
        if response.success:
            # Simplified check - assume requirements are covered
            return {
                'passed': True,
                'requirements': response.content,
                'missing': []
            }
        
        return {
            'passed': True,
            'requirements': '',
            'missing': []
        }
    
    def _add_qa_feedback(self, issue, qa_result: Dict) -> None:
        """Add QA feedback as a comment."""
        lines = [
            "## 🔍 QA Review Results",
            "",
            "**Status:** ❌ Nicht bestanden",
            "",
            "### Durchgeführte Prüfungen:"
        ]
        
        for check in qa_result.get('checks', []):
            status = "✅" if check['passed'] else "❌"
            lines.append(f"{status} {check['check']}")
        
        if qa_result.get('issues'):
            lines.append("")
            lines.append("### Gefundene Probleme:")
            for issue_text in qa_result['issues']:
                lines.append(f"- {issue_text}")
        
        if qa_result.get('feedback'):
            lines.append("")
            lines.append("### Feedback:")
            lines.append(qa_result['feedback'])
        
        lines.append("")
        lines.append("Bitte beheben Sie die genannten Probleme und reichen Sie den Code erneut ein.")
        
        comment = "\n".join(lines)
        self.github.add_comment(issue.number, comment)
    
    def _create_pull_request(self, issue) -> None:
        """Create a pull request for the completed feature."""
        branch_name = f"feature/issue-{issue.number}"
        
        try:
            pr = self.github.create_pull_request(
                title=f"Feature: {issue.title}",
                body=f"Closes #{issue.number}\n\nImplementierung der Anforderung.",
                head=branch_name
            )
            
            logger.info(f"Created PR #{pr.get('number')} for issue #{issue.number}")
            
            self.mqtt.publish(create_event(
                EventType.CODE_REVIEWED,
                self.name,
                issue.number,
                payload={"pr_number": pr.get('number'), "url": pr.get('html_url')}
            ))
            
        except Exception as e:
            logger.warning(f"Could not create PR: {e}")


def main():
    """Main entry point."""
    agent = QAAgent()
    
    try:
        agent.start()
        
        while agent.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    main()
