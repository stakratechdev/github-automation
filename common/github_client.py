"""
GitHub Client for API Interaction.
Handles issue management, comments, labels, and commits.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config_loader import GitHubConfig, get_config
from .event_types import IssueStatus, StatusManager

logger = logging.getLogger(__name__)


@dataclass
class GitHubIssue:
    """Represents a GitHub issue."""
    number: int
    title: str
    body: str
    state: str
    labels: List[str]
    created_at: str
    updated_at: str
    html_url: str
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'GitHubIssue':
        """Create GitHubIssue from API response."""
        labels = [label['name'] for label in data.get('labels', [])]
        
        return cls(
            number=data['number'],
            title=data['title'],
            body=data['body'] or "",
            state=data['state'],
            labels=labels,
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            html_url=data['html_url']
        )


@dataclass
class GitHubComment:
    """Represents a GitHub issue comment."""
    id: int
    body: str
    user: str
    created_at: str
    
    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'GitHubComment':
        """Create GitHubComment from API response."""
        return cls(
            id=data['id'],
            body=data['body'],
            user=data['user']['login'],
            created_at=data['created_at']
        )


class GitHubClient:
    """
    Client for GitHub API interactions.
    
    Features:
    - Issue management (create, update, list)
    - Comment management
    - Label management
    - Branch and commit operations
    """
    
    def __init__(self, config: Optional[GitHubConfig] = None):
        """Initialize GitHub client."""
        self.config = config or get_config().github
        
        # Set up session with retry strategy
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Set headers
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.config.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        self.base_url = self.config.api_url
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make an authenticated API request."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API error: {e}")
            raise
    
    # Issue Operations
    
    def get_issues(
        self,
        state: str = "open",
        labels: Optional[List[str]] = None,
        since: Optional[str] = None
    ) -> List[GitHubIssue]:
        """
        Get list of issues.
        
        Args:
            state: Issue state (open, closed, all)
            labels: Filter by labels
            since: Filter by date
            
        Returns:
            List of GitHubIssue objects
        """
        params = {"state": state}
        
        if labels:
            params["labels"] = ",".join(labels)
        
        if since:
            params["since"] = since
        
        data = self._request("GET", f"/repos/{self.config.owner}/{self.config.repo}/issues", params=params)
        
        return [GitHubIssue.from_api(item) for item in data]
    
    def get_issue(self, issue_number: int) -> Optional[GitHubIssue]:
        """
        Get a single issue.
        
        Args:
            issue_number: Issue number
            
        Returns:
            GitHubIssue or None
        """
        try:
            data = self._request(
                "GET",
                f"/repos/{self.config.owner}/{self.config.repo}/issues/{issue_number}"
            )
            return GitHubIssue.from_api(data)
        except requests.exceptions.HTTPError:
            return None
    
    def get_issue_status(self, issue_number: int) -> IssueStatus:
        """
        Get the status of an issue based on labels.
        
        Args:
            issue_number: Issue number
            
        Returns:
            IssueStatus
        """
        issue = self.get_issue(issue_number)
        if issue is None:
            return IssueStatus.NEW
        
        return StatusManager.get_status_from_labels(issue.labels)
    
    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[List[str]] = None
    ) -> GitHubIssue:
        """
        Create a new issue.
        
        Args:
            title: Issue title
            body: Issue body
            labels: Initial labels
            
        Returns:
            Created GitHubIssue
        """
        data = {"title": title, "body": body}
        
        if labels:
            data["labels"] = labels
        
        result = self._request(
            "POST",
            f"/repos/{self.config.owner}/{self.config.repo}/issues",
            data=data
        )
        
        return GitHubIssue.from_api(result)
    
    def update_issue(
        self,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None
    ) -> GitHubIssue:
        """
        Update an existing issue.
        
        Args:
            issue_number: Issue number
            title: New title
            body: New body
            state: New state (open, closed)
            
        Returns:
            Updated GitHubIssue
        """
        data = {}
        
        if title:
            data["title"] = title
        
        if body:
            data["body"] = body
        
        if state:
            data["state"] = state
        
        result = self._request(
            "PATCH",
            f"/repos/{self.config.owner}/{self.config.repo}/issues/{issue_number}",
            data=data
        )
        
        return GitHubIssue.from_api(result)
    
    def add_labels(self, issue_number: int, labels: List[str]) -> List[str]:
        """
        Add labels to an issue.
        
        Args:
            issue_number: Issue number
            labels: Labels to add
            
        Returns:
            List of current labels
        """
        result = self._request(
            "POST",
            f"/repos/{self.config.owner}/{self.config.repo}/issues/{issue_number}/labels",
            data={"labels": labels}
        )
        
        return [label['name'] for label in result]
    
    def remove_label(self, issue_number: int, label: str) -> bool:
        """
        Remove a label from an issue.
        
        Args:
            issue_number: Issue number
            label: Label to remove
            
        Returns:
            True if successful
        """
        try:
            self._request(
                "DELETE",
                f"/repos/{self.config.owner}/{self.config.repo}/issues/{issue_number}/labels/{label}"
            )
            return True
        except requests.exceptions.HTTPError:
            return False
    
    def set_status_label(self, issue_number: int, status: IssueStatus) -> None:
        """
        Set issue status by adding/removing status labels.
        
        Args:
            issue_number: Issue number
            status: Target status
        """
        # Remove all status labels
        current_labels = self.get_issue(issue_number).labels
        status_labels = list(StatusManager.STATUS_LABELS.values())
        
        labels_to_remove = [l for l in current_labels if l in status_labels]
        for label in labels_to_remove:
            self.remove_label(issue_number, label)
        
        # Add new status label
        new_label = StatusManager.get_label_for_status(status)
        if new_label:
            self.add_labels(issue_number, [new_label])
    
    # Comment Operations
    
    def get_comments(self, issue_number: int) -> List[GitHubComment]:
        """
        Get comments for an issue.
        
        Args:
            issue_number: Issue number
            
        Returns:
            List of GitHubComment objects
        """
        data = self._request(
            "GET",
            f"/repos/{self.config.owner}/{self.config.repo}/issues/{issue_number}/comments"
        )
        
        return [GitHubComment.from_api(item) for item in data]
    
    def add_comment(self, issue_number: int, body: str) -> GitHubComment:
        """
        Add a comment to an issue.
        
        Args:
            issue_number: Issue number
            body: Comment body
            
        Returns:
            Created GitHubComment
        """
        result = self._request(
            "POST",
            f"/repos/{self.config.owner}/{self.config.repo}/issues/{issue_number}/comments",
            data={"body": body}
        )
        
        return GitHubComment.from_api(result)
    
    def update_comment(
        self,
        issue_number: int,
        comment_id: int,
        body: str
    ) -> GitHubComment:
        """
        Update a comment.
        
        Args:
            issue_number: Issue number
            comment_id: Comment ID
            body: New comment body
            
        Returns:
            Updated GitHubComment
        """
        result = self._request(
            "PATCH",
            f"/repos/{self.config.owner}/{self.config.repo}/issues/comments/{comment_id}",
            data={"body": body}
        )
        
        return GitHubComment.from_api(result)
    
    def delete_comment(self, issue_number: int, comment_id: int) -> bool:
        """
        Delete a comment.
        
        Args:
            issue_number: Issue number
            comment_id: Comment ID
            
        Returns:
            True if successful
        """
        try:
            self._request(
                "DELETE",
                f"/repos/{self.config.owner}/{self.config.repo}/issues/comments/{comment_id}"
            )
            return True
        except requests.exceptions.HTTPError:
            return False
    
    # Branch and Commit Operations
    
    def get_branch(self, branch: str) -> Dict:
        """
        Get branch information.
        
        Args:
            branch: Branch name
            
        Returns:
            Branch data
        """
        return self._request(
            "GET",
            f"/repos/{self.config.owner}/{self.config.repo}/branches/{branch}"
        )
    
    def create_branch(self, branch_name: str, from_branch: str = "main") -> Dict:
        """
        Create a new branch from an existing branch.
        
        Args:
            branch_name: Name of new branch
            from_branch: Source branch
            
        Returns:
            Created branch data
        """
        # Get SHA of source branch
        source = self.get_branch(from_branch)
        sha = source['commit']['sha']
        
        # Create new branch
        return self._request(
            "POST",
            f"/repos/{self.config.owner}/{self.config.repo}/git/refs",
            data={
                "ref": f"refs/heads/{branch_name}",
                "sha": sha
            }
        )
    
    def get_file_content(self, path: str, branch: str = "main") -> str:
        """
        Get file content from repository.
        
        Args:
            path: File path
            branch: Branch name
            
        Returns:
            File content as string
        """
        result = self._request(
            "GET",
            f"/repos/{self.config.owner}/{self.config.repo}/contents/{path}",
            params={"ref": branch}
        )
        
        import base64
        return base64.b64decode(result['content']).decode('utf-8')
    
    def create_or_update_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: str,
        sha: Optional[str] = None
    ) -> Dict:
        """
        Create or update a file in the repository.
        
        Args:
            path: File path
            content: File content
            message: Commit message
            branch: Target branch
            sha: SHA of existing file (for updates)
            
        Returns:
            Commit data
        """
        import base64
        
        data = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode('utf-8'),
            "branch": branch
        }
        
        if sha:
            data["sha"] = sha
        
        return self._request(
            "PUT",
            f"/repos/{self.config.owner}/{self.config.repo}/contents/{path}",
            data=data
        )
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict:
        """
        Create a pull request.
        
        Args:
            title: PR title
            body: PR body
            head: Source branch
            base: Target branch
            
        Returns:
            PR data
        """
        return self._request(
            "POST",
            f"/repos/{self.config.owner}/{self.config.repo}/pulls",
            data={
                "title": title,
                "body": body,
                "head": head,
                "base": base
            }
        )
    
    def close_issue(self, issue_number: int) -> GitHubIssue:
        """
        Close an issue.
        
        Args:
            issue_number: Issue number
            
        Returns:
            Updated GitHubIssue
        """
        return self.update_issue(issue_number, state="closed")


def get_github_client() -> GitHubClient:
    """Factory function to get a configured GitHub client."""
    return GitHubClient()
