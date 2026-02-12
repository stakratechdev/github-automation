"""
Event Types and Structures for GitHub Automation Architecture.
Defines the event schema and status signals for agent communication.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import json


class EventType(Enum):
    """Types of events in the automation system."""
    ISSUE_CREATED = "issue_created"
    ISSUE_UPDATED = "issue_updated"
    ISSUE_CLOSED = "issue_closed"
    ISSUE_REOPENED = "issue_reopened"
    COMMENT_ADDED = "comment_added"
    LABEL_CHANGED = "label_changed"
    STATUS_CHANGED = "status_changed"
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    AGENT_ERROR = "agent_error"
    CODE_GENERATED = "code_generated"
    CODE_COMMITTED = "code_committed"
    CODE_REVIEWED = "code_reviewed"
    QA_PASSED = "qa_passed"
    QA_FAILED = "qa_failed"


class IssueStatus(Enum):
    """Status states for issues in the workflow."""
    NEW = "new"
    WAITING_FOR_CLARIFICATION = "waiting_for_clarification"
    READY_FOR_DEV = "ready_for_dev"
    IN_PROGRESS = "in_progress"
    READY_FOR_QA = "ready_for_qa"
    DONE = "done"
    BLOCKED = "blocked"


# Status to Label mapping
STATUS_LABELS = {
    IssueStatus.NEW: "needs-analysis",
    IssueStatus.WAITING_FOR_CLARIFICATION: "waiting_for_clarification",
    IssueStatus.READY_FOR_DEV: "ready_for_dev",
    IssueStatus.IN_PROGRESS: "in_progress",
    IssueStatus.READY_FOR_QA: "ready_for_qa",
    IssueStatus.DONE: "done",
    IssueStatus.BLOCKED: "blocked",
}


@dataclass
class AgentEvent:
    """
    Base event structure for all agent events.
    
    Attributes:
        event_type: Type of the event
        agent_name: Name of the agent that triggered the event
        timestamp: When the event occurred
        issue_number: Related GitHub issue number (if applicable)
        payload: Additional event-specific data
    """
    event_type: EventType
    agent_name: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    issue_number: Optional[int] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps({
            'event_type': self.event_type.value,
            'agent_name': self.agent_name,
            'timestamp': self.timestamp,
            'issue_number': self.issue_number,
            'payload': self.payload
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentEvent':
        """Deserialize event from JSON."""
        data = json.loads(json_str)
        return cls(
            event_type=EventType(data['event_type']),
            agent_name=data['agent_name'],
            timestamp=data['timestamp'],
            issue_number=data.get('issue_number'),
            payload=data.get('payload', {})
        )


def create_event(
    event_type: EventType,
    agent_name: str,
    issue_number: Optional[int] = None,
    **kwargs
) -> AgentEvent:
    """
    Factory function to create an AgentEvent.
    
    Args:
        event_type: Type of event
        agent_name: Name of the agent
        issue_number: Related issue number
        **kwargs: Additional payload data
        
    Returns:
        AgentEvent instance
    """
    return AgentEvent(
        event_type=event_type,
        agent_name=agent_name,
        issue_number=issue_number,
        payload=kwargs
    )


class EventPublisher:
    """
    Interface for publishing events.
    Implementations should use MQTT or similar messaging system.
    """
    
    def publish(self, event: AgentEvent) -> bool:
        """Publish an event to the messaging system."""
        raise NotImplementedError
    
    def subscribe(self, callback) -> None:
        """Subscribe to events."""
        raise NotImplementedError
    
    def disconnect(self) -> None:
        """Disconnect from the messaging system."""
        raise NotImplementedError


class StatusManager:
    """
    Manages issue status transitions.
    Provides helper methods for status-related operations.
    """
    
    @staticmethod
    def get_label_for_status(status: IssueStatus) -> str:
        """Get the GitHub label for a given status."""
        return STATUS_LABELS.get(status, "")
    
    @staticmethod
    def get_status_from_labels(labels: list[str]) -> IssueStatus:
        """Determine issue status from GitHub labels."""
        label_to_status = {v: k for k, v in STATUS_LABELS.items()}
        
        for label in labels:
            if label in label_to_status:
                return label_to_status[label]
        
        return IssueStatus.NEW
    
    @staticmethod
    def is_ready_for_transition(
        current_status: IssueStatus,
        target_status: IssueStatus
    ) -> bool:
        """
        Check if a status transition is valid.
        
        Valid transitions:
        - NEW -> WAITING_FOR_CLARIFICATION
        - NEW -> READY_FOR_DEV
        - WAITING_FOR_CLARIFICATION -> READY_FOR_DEV
        - READY_FOR_DEV -> IN_PROGRESS
        - IN_PROGRESS -> READY_FOR_QA
        - IN_PROGRESS -> BLOCKED
        - BLOCKED -> IN_PROGRESS
        - READY_FOR_QA -> DONE
        - READY_FOR_QA -> IN_PROGRESS (if QA fails)
        """
        valid_transitions = {
            IssueStatus.NEW: [
                IssueStatus.WAITING_FOR_CLARIFICATION,
                IssueStatus.READY_FOR_DEV
            ],
            IssueStatus.WAITING_FOR_CLARIFICATION: [
                IssueStatus.READY_FOR_DEV
            ],
            IssueStatus.READY_FOR_DEV: [
                IssueStatus.IN_PROGRESS
            ],
            IssueStatus.IN_PROGRESS: [
                IssueStatus.READY_FOR_QA,
                IssueStatus.BLOCKED
            ],
            IssueStatus.BLOCKED: [
                IssueStatus.IN_PROGRESS
            ],
            IssueStatus.READY_FOR_QA: [
                IssueStatus.DONE,
                IssueStatus.IN_PROGRESS
            ]
        }
        
        return target_status in valid_transitions.get(current_status, [])
