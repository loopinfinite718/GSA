"""
GitLab API client for retrieving merge request and review data.

This module provides a clean interface for interacting with the GitLab API,
abstracting away the details of API calls and data transformation.
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

import gitlab
from gitlab.v4.objects import Project, MergeRequest

from data_models import ReviewComment, ApprovalStatus, SentimentScore


class GitLabClient:
    """Client for interacting with the GitLab API."""
    
    def __init__(self, gitlab_url: str, private_token: str, project_id: str):
        """Initialize the GitLab client.
        
        Args:
            gitlab_url: GitLab instance URL
            private_token: GitLab private access token
            project_id: GitLab project ID
        """
        self.gitlab_url = gitlab_url
        self.private_token = private_token
        self.project_id = project_id
        self.gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        self.project = self.gl.projects.get(project_id)
    
    @classmethod
    def from_env(cls) -> 'GitLabClient':
        """Create a GitLabClient instance from environment variables.
        
        Returns:
            GitLabClient instance
        
        Raises:
            ValueError: If required environment variables are missing
        """
        gitlab_url = os.getenv('GITLAB_URL')
        private_token = os.getenv('GITLAB_TOKEN')
        project_id = os.getenv('GITLAB_PROJECT_ID')
        
        if not all([gitlab_url, private_token, project_id]):
            missing = []
            if not gitlab_url:
                missing.append('GITLAB_URL')
            if not private_token:
                missing.append('GITLAB_TOKEN')
            if not project_id:
                missing.append('GITLAB_PROJECT_ID')
            
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return cls(gitlab_url, private_token, project_id)
    
    def get_merge_requests(self, since_date: datetime) -> List[MergeRequest]:
        """Get merge requests since a specific date.
        
        Args:
            since_date: Date from which to fetch MRs
            
        Returns:
            List of merge request objects
        """
        mrs = self.project.mergerequests.list(
            state='all',
            created_after=since_date.isoformat(),
            all=True
        )
        return mrs
    
    def get_mr_reviews(self, mr: MergeRequest, 
                       sentiment_analyzer: Any) -> List[ReviewComment]:
        """Get all review comments for a merge request with sentiment analysis.
        
        Args:
            mr: Merge request object
            sentiment_analyzer: Object with analyze_sentiment method
            
        Returns:
            List of ReviewComment objects
        """
        comments = []
        
        # Get notes (comments)
        notes = mr.notes.list(all=True)
        
        for note in notes:
            if note.system:  # Skip system notes
                continue
                
            # Analyze sentiment
            textblob_sentiment, vader_sentiment = sentiment_analyzer.analyze_sentiment(note.body)
            
            # Determine approval status based on note content
            approval_status = self._determine_approval_status(note, mr)
            
            # Create sentiment score object
            sentiment = SentimentScore(
                textblob_score=textblob_sentiment,
                vader_compound=vader_sentiment.get('compound', 0.0),
                vader_positive=vader_sentiment.get('pos', 0.0),
                vader_neutral=vader_sentiment.get('neu', 0.0),
                vader_negative=vader_sentiment.get('neg', 0.0)
            )
            
            # Parse created_at datetime
            created_at = datetime.fromisoformat(
                note.created_at.replace('Z', '+00:00')
            )
            
            comment = ReviewComment(
                id=str(note.id),
                author=note.author.get('name', 'Unknown'),
                body=note.body,
                created_at=created_at,
                mr_id=mr.id,
                mr_title=mr.title,
                mr_author=mr.author.get('name', 'Unknown'),
                sentiment=sentiment,
                approval_status=approval_status
            )
            comments.append(comment)
            
        return comments
    
    def _determine_approval_status(self, note: Any, mr: MergeRequest) -> ApprovalStatus:
        """Determine if a review comment represents approval, requested changes, or just a comment.
        
        Args:
            note: Note object from GitLab
            mr: Merge request object
            
        Returns:
            ApprovalStatus enum value
        """
        # Check if this note contains approval/request changes indicators
        body_lower = note.body.lower()
        
        # Look for approval indicators
        approval_keywords = [
            'approved', 'lgtm', 'looks good', 'approve', 'ship it',
            ':+1:', '👍', ':thumbsup:', 'ready to merge'
        ]
        
        # Look for request changes indicators
        changes_keywords = [
            'request changes', 'needs changes', 'please fix', 'fix this',
            'don\'t merge', 'not ready', 'block', 'blocking', 'nack',
            ':-1:', '👎', ':thumbsdown:'
        ]
        
        if any(keyword in body_lower for keyword in approval_keywords):
            return ApprovalStatus.APPROVED
        elif any(keyword in body_lower for keyword in changes_keywords):
            return ApprovalStatus.REQUESTED_CHANGES
        else:
            return ApprovalStatus.COMMENTED
    
    def get_mr_details(self, mr: MergeRequest) -> Dict[str, Any]:
        """Get additional details about a merge request.
        
        Args:
            mr: Merge request object
            
        Returns:
            Dictionary with additional MR details
        """
        # Calculate review and merge times
        created_at = datetime.fromisoformat(mr.created_at.replace('Z', '+00:00'))
        
        details = {
            'id': mr.id,
            'title': mr.title,
            'state': mr.state,
            'created_at': created_at,
            'author': mr.author.get('name', 'Unknown'),
            'changes_count': mr.changes_count,
            'commits': []
        }
        
        # Add merge time if available
        if hasattr(mr, 'merged_at') and mr.merged_at:
            merged_at = datetime.fromisoformat(mr.merged_at.replace('Z', '+00:00'))
            details['merged_at'] = merged_at
            details['merge_time_hours'] = (merged_at - created_at).total_seconds() / 3600
        
        # Add updated time
        if hasattr(mr, 'updated_at') and mr.updated_at:
            updated_at = datetime.fromisoformat(mr.updated_at.replace('Z', '+00:00'))
            details['updated_at'] = updated_at
            details['review_time_hours'] = (updated_at - created_at).total_seconds() / 3600
        
        # Get commits if available
        try:
            commits = mr.commits()
            details['commits'] = [
                {
                    'id': commit.id,
                    'title': commit.title,
                    'author_name': commit.author_name,
                    'created_at': commit.created_at
                }
                for commit in commits
            ]
        except Exception:
            # Commits might not be available for all MRs
            pass
        
        return details