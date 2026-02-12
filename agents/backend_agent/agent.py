"""
Backend Agent for GitHub Automation.
Generates backend code based on requirements.
"""

import logging
import time
import threading
import re
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


class BackendAgent:
    """
    Backend Agent.
    
    Responsibilities:
    - Monitor issues with "backend" label
    - Generate backend code using LLM
    - Create API endpoints, models, services
    - Follow backend coding patterns
    """
    
    def __init__(
        self,
        agent_config: Optional[AgentConfig] = None,
        github_client: Optional[GitHubClient] = None,
        mqtt_client: Optional[MQTTClient] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """Initialize the Backend Agent."""
        self.config = agent_config or get_config().agents.get(
            'backend_agent',
            AgentConfig(name="backend-agent")
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
            payload={"agent_type": "backend"}
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
            payload={"agent_type": "backend"}
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
        """Process issues ready for backend development."""
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
        """Process a single backend issue."""
        logger.info(f"Processing backend issue #{issue.number}: {issue.title}")
        
        self._processing_issues[issue.number] = "in_progress"
        
        self.mqtt.publish(create_event(
            EventType.STATUS_CHANGED,
            self.name,
            issue.number,
            payload={"action": "backend_dev_started", "title": issue.title}
        ))
        
        self.github.set_status_label(issue.number, IssueStatus.IN_PROGRESS)
        
        try:
            # Generate backend code
            code_files = self._generate_backend_code(issue)
            
            # Create branch and commit
            branch_name = f"backend/issue-{issue.number}-{self._sanitize_branch(issue.title)}"
            self._create_and_commit(issue, branch_name, code_files)
            
            # Update status
            self.github.set_status_label(issue.number, IssueStatus.READY_FOR_QA)
            
            self.mqtt.publish(create_event(
                EventType.CODE_GENERATED,
                self.name,
                issue.number,
                payload={
                    "action": "backend_completed",
                    "files_generated": list(code_files.keys()),
                    "branch": branch_name
                }
            ))
            
            logger.info(f"Backend development completed for issue #{issue.number}")
            
        except Exception as e:
            logger.error(f"Error in backend development: {e}")
        
        finally:
            del self._processing_issues[issue.number]
    
    def _generate_backend_code(self, issue) -> Dict[str, str]:
        """Generate backend code for the issue."""
        structure = self._get_repository_structure()
        
        prompt = self._create_code_prompt(issue)
        
        response = self.llm.generate_code(
            prompt=prompt,
            context=structure
        )
        
        if not response.success:
            raise Exception(f"Code generation failed: {response.error}")
        
        return self._parse_code_response(response.content, issue)
    
    def _get_repository_structure(self) -> str:
        """Get backend repository structure."""
        try:
            guidelines = self.github.get_file_content(
                ".github/CODING_GUIDELINES.md"
            )
        except:
            guidelines = "Follow REST API best practices."
        
        return f"""
Backend Coding Guidelines:
{guidelines}

Backend Structure:
backend/
  src/
    controllers/
    models/
    services/
    middleware/
  api/
  tests/

Technology: Python/FastAPI or Node.js/Express
"""
    
    def _create_code_prompt(self, issue) -> str:
        """Create prompt for backend code generation."""
        return f"""
Generate backend code for the following GitHub issue:

## Issue #{issue.number}: {issue.title}

{issue.body}

Requirements:
1. Create RESTful API endpoints
2. Include data models
3. Add error handling and validation
4. Include unit tests
5. Follow backend best practices

Return the code in format:
=== filename ===
[code here]
"""
    
    def _parse_code_response(self, response: str, issue) -> Dict[str, str]:
        """Parse code generation response into files."""
        files = {}
        
        current_file = None
        current_content = []
        
        lines = response.split('\n')
        for line in lines:
            if line.startswith('===') and line.endswith('==='):
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                current_file = line[4:-4].strip()
                current_content = []
            elif current_file:
                current_content.append(line)
        
        if current_file:
            files[current_file] = '\n'.join(current_content)
        
        if not files:
            files[f"backend_issue_{issue.number}.py"] = response
        
        return files
    
    def _sanitize_branch(self, title: str) -> str:
        """Create valid branch name."""
        branch = title.lower()
        branch = re.sub(r'[^a-z0-9\-]', '', branch)
        return branch[:50]
    
    def _create_and_commit(self, issue, branch_name: str, files: Dict[str, str]) -> None:
        """Create branch and commit code changes."""
        try:
            self.github.create_branch(branch_name)
            logger.info(f"Created branch: {branch_name}")
        except Exception as e:
            logger.warning(f"Branch might already exist: {e}")
        
        for path, content in files.items():
            try:
                self.github.create_or_update_file(
                    path=path,
                    content=content,
                    message=f"feat(backend): {issue.title}\n\nGenerated by Backend Agent",
                    branch=branch_name
                )
                logger.info(f"Committed: {path}")
            except Exception as e:
                logger.error(f"Error committing {path}: {e}")
        
        self.mqtt.publish(create_event(
            EventType.CODE_COMMITTED,
            self.name,
            issue.number,
            payload={"branch": branch_name, "files_count": len(files)}
        ))


def main():
    """Main entry point."""
    agent = BackendAgent()
    
    try:
        agent.start()
        
        while agent.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        agent.stop()


if __name__ == "__main__":
    main()
