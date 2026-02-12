"""
GitHub Automation Agents.

This package contains the multi-agent system for automated software development.

Agents:
- Requirements Engineer: Analyzes and clarifies requirements
- Frontend Agent: Generates frontend code
- Backend Agent: Generates backend code
- QA Agent: Validates and tests code
"""

from .requirements_engineer.agent import RequirementsEngineerAgent
from .frontend_agent.agent import FrontendAgent
from .backend_agent.agent import BackendAgent
from .qa_agent.agent import QAAgent

__all__ = [
    'RequirementsEngineerAgent',
    'FrontendAgent',
    'BackendAgent',
    'QAAgent'
]
