"""
Frontend Agent for GitHub Automation.
Generates frontend code based on requirements.
"""

import logging
import time
import threading
from datetime import datetime
from typing import Dict, Optional

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


class FrontendAgent:
    """
    Frontend Agent.
    
    Responsibilities:
    - Monitor issues with "frontend" label
    - Generate frontend code using LLM
    - Create feature branches
    - Commit code changes
    - Update issue status
    """
    
    def __init__(
        self,
        agent_config: Optional[AgentConfig] = None,
        github_client: Optional[GitHubClient] = None,
        mqtt_client: Optional[MQTTClient] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """Initialize the Frontend Agent."""
        self.config = agent_config or get_config().agents.get(
            'frontend_agent',
            AgentConfig(name="frontend-agent")
        )
        
        self.github = github_client or GitHubClient()
        self.mqtt = mqtt_client or MQTTClient()
        self.llm = llm_client or LLMClient()
        
        self.name = self.config.name
        self.running = False
        self._stop_event = threading.Event()
        
        # Track in-progress issues
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
            payload={"agent_type": "frontend"}
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
            payload={"agent_type": "frontend"}
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
            
            self._stop_event.wait(self.config.poll_interval)
    
    def _process_issues(self) -> None:
        """Process issues ready for frontend development."""
        ready_label = self.config.labels.ready
        
        # Get issues ready for development
        issues = self.github.get_issues(state="open", labels=[ready_label])
        
        for issue in issues:
            if self._stop_event.is_set():
                break
            
            # Skip issues already being processed
            if issue.number in self._processing_issues:
                continue
            
            try:
                self._process_issue(issue)
            except Exception as e:
                logger.error(f"Error processing issue #{issue.number}: {e}")
    
    def _process_issue(self, issue: GitHubIssue) -> None:
        """Process a single frontend issue."""
        logger.info(f"Processing frontend issue #{issue.number}: {issue.title}")
        
        # Track this issue
        self._processing_issues[issue.number] = "in_progress"
        
        # Publish started event
        self.mqtt.publish(create_event(
            EventType.STATUS_CHANGED,
            self.name,
            issue.number,
            payload={"action": "frontend_dev_started", "title": issue.title}
        ))
        
        # Update status to in_progress
        self.github.set_status_label(issue.number, IssueStatus.IN_PROGRESS)
        
        try:
            # Generate frontend code
            code_files = self._generate_frontend_code(issue)
            
            # Create branch and commit changes
            branch_name = f"feature/issue-{issue.number}-{self._sanitize_branch(issue.title)}"
            self._create_and_commit(issue, branch_name, code_files)
            
            # Update issue status
            ready_qa_label = self.config.labels.ready
            if ready_qa_label:
                self.github.add_labels(issue.number, [ready_qa_label])
            
            self.github.set_status_label(issue.number, IssueStatus.READY_FOR_QA)
            
            # Publish completion event
            self.mqtt.publish(create_event(
                EventType.CODE_GENERATED,
                self.name,
                issue.number,
                payload={
                    "action": "frontend_completed",
                    "files_generated": list(code_files.keys()),
                    "branch": branch_name
                }
            ))
            
            logger.info(f"Frontend development completed for issue #{issue.number}")
            
        except Exception as e:
            logger.error(f"Error in frontend development: {e}")
            self.mqtt.publish(create_event(
                EventType.AGENT_ERROR,
                self.name,
                issue.number,
                payload={"error": str(e)}
            ))
        
        finally:
            del self._processing_issues[issue.number]
    
    def _generate_frontend_code(self, issue: GitHubIssue) -> Dict[str, str]:
        """Generate frontend code for the issue."""
        # Get existing code structure
        structure = self._get_repository_structure()
        
        # Generate code using LLM
        prompt = self._create_code_prompt(issue)
        
        response = self.llm.generate_code(
            prompt=prompt,
            context=structure
        )
        
        if not response.success:
            raise Exception(f"Code generation failed: {response.error}")
        
        # Parse response and split into files
        return self._parse_code_response(response.content, issue)
    
    def _get_repository_structure(self) -> str:
        """Get repository structure for context."""
        try:
            # Try to read coding guidelines
            guidelines = self.github.get_file_content(
                ".github/CODING_GUIDELINES.md"
            )
        except:
            guidelines = "Follow Flutter best practices."
        
        try:
            # Get existing frontend structure
            structure = self.github.get_file_content(
                "frontend/",
                branch="main"
            )
        except:
            structure = "frontend/lib/"
        
        return f"""
Repository Structure Guidelines:
{guidelines}

Frontend Directory Structure:
frontend/
  lib/
    main.dart
    screens/
    widgets/
    models/
    services/
  pubspec.yaml

Please generate Flutter code following these guidelines.
"""
    
    def _create_code_prompt(self, issue: GitHubIssue) -> str:
        """Create prompt for code generation."""
        return f"""
Generate frontend code for the following GitHub issue:

## Issue #{issue.number}: {issue.title}

{issue.body}

Requirements:
1. Generate complete, working Flutter code
2. Follow clean architecture principles
3. Include proper error handling
4. Add unit tests if applicable

Return the code in the following format for each file:
```
=== filename.dart ===
[code here]
```

Files to generate (if applicable):
- UI components
- State management
- Service layer
- Models
"""
    
    def _parse_code_response(self, response: str, issue: GitHubIssue) -> Dict[str, str]:
        """Parse code generation response into files."""
        files = {}
        
        # Split by file markers
        current_file = None
        current_content = []
        
        lines = response.split('\n')
        for line in lines:
            if line.startswith('===') and line.endswith('==='):
                # Save previous file
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                
                # Start new file
                current_file = line[4:-4].strip()
                current_content = []
            elif current_file:
                current_content.append(line)
        
        # Save last file
        if current_file:
            files[current_file] = '\n'.join(current_content)
        
        # If no file markers found, create a single file
        if not files:
            files[f"issue_{issue.number}.dart"] = response
        
        return files
    
    def _sanitize_branch(self, title: str) -> str:
        """Create a valid branch name from title."""
        import re
        # Replace spaces with hyphens, remove special chars
        branch = title.lower()
        branch = re.sub(r'[^a-z0-9\-]', '', branch)
        branch = branch[:50]  # Limit length
        return branch
    
    def _create_and_commit(
        self,
        issue: GitHubIssue,
        branch_name: str,
        files: Dict[str, str]
    ) -> None:
        """Create branch and commit code changes."""
        # Create feature branch
        try:
            self.github.create_branch(branch_name)
            logger.info(f"Created branch: {branch_name}")
        except Exception as e:
            logger.warning(f"Branch might already exist: {e}")
        
        # Commit each file
        for path, content in files.items():
            try:
                # Try to get existing file SHA
                try:
                    existing = self.github.get_file_content(path, branch_name)
                    sha = existing.get('sha') if isinstance(existing, dict) else None
                except:
                    sha = None
                
                self.github.create_or_update_file(
                    path=path,
                    content=content,
                    message=f"feat(#{issue.number}): {issue.title}\n\nGenerated by Frontend Agent",
                    branch=branch_name,
                    sha=sha
                )
                logger.info(f"Committed: {path}")
                
            except Exception as e:
                logger.error(f"Error committing {path}: {e}")
        
        # Publish commit event
        self.mqtt.publish(create_event(
            EventType.CODE_COMMITTED,
            self.name,
            issue.number,
            payload={
                "branch": branch_name,
                "files_count": len(files)
            }
        ))


def main():
    """Main entry point for the agent."""
    agent = FrontendAgent()
    
    try:
        agent.start()
        
        while agent.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    main()
