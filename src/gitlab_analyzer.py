"""
GitLab MR Review Sentiment Analyzer

This module provides functionality to analyze GitLab merge request reviews,
including sentiment analysis and reviewer behavior patterns.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

import gitlab
import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import ollama


@dataclass
class ReviewComment:
    """Data class for storing review comment information."""
    author: str
    body: str
    created_at: datetime
    mr_id: int
    mr_title: str
    mr_author: str
    sentiment_textblob: float
    sentiment_vader: Dict[str, float]
    approval_status: str  # 'approved', 'requested_changes', 'commented'


@dataclass
class ReviewerStats:
    """Data class for storing reviewer statistics."""
    reviewer_name: str
    total_reviews: int
    approved_count: int
    requested_changes_count: int
    comment_only_count: int
    avg_sentiment_textblob: float
    avg_sentiment_vader: Dict[str, float]
    reviewed_authors: Dict[str, int]
    sentiment_by_author: Dict[str, List[float]]


class GitLabAnalyzer:
    """Main class for analyzing GitLab merge request reviews."""
    
    def __init__(self, gitlab_url: str, private_token: str, project_id: str):
        """Initialize the GitLab analyzer.
        
        Args:
            gitlab_url: GitLab instance URL
            private_token: GitLab private access token
            project_id: GitLab project ID
        """
        self.gl = gitlab.Gitlab(gitlab_url, private_token=private_token)
        self.project = self.gl.projects.get(project_id)
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
    def get_merge_requests(self, since_date: datetime) -> List:
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
    
    def analyze_sentiment(self, text: str) -> Tuple[float, Dict[str, float]]:
        """Analyze sentiment of text using multiple methods.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (TextBlob polarity, VADER scores)
        """
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment.polarity
        
        # VADER sentiment
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        return textblob_sentiment, vader_scores
    
    def get_mr_reviews(self, mr) -> List[ReviewComment]:
        """Get all review comments for a merge request.
        
        Args:
            mr: Merge request object
            
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
            textblob_sentiment, vader_sentiment = self.analyze_sentiment(note.body)
            
            # Determine approval status based on note content and system events
            approval_status = self._determine_approval_status(note, mr)
            
            comment = ReviewComment(
                author=note.author.get('name', 'Unknown'),
                body=note.body,
                created_at=datetime.fromisoformat(note.created_at.replace('Z', '+00:00')),
                mr_id=mr.id,
                mr_title=mr.title,
                mr_author=mr.author.get('name', 'Unknown'),
                sentiment_textblob=textblob_sentiment,
                sentiment_vader=vader_sentiment,
                approval_status=approval_status
            )
            comments.append(comment)
            
        return comments
    
    def _determine_approval_status(self, note, mr) -> str:
        """Determine if a review comment represents approval, requested changes, or just a comment.
        
        Args:
            note: Note object from GitLab
            mr: Merge request object
            
        Returns:
            String indicating approval status
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
            return 'approved'
        elif any(keyword in body_lower for keyword in changes_keywords):
            return 'requested_changes'
        else:
            return 'commented'
    
    def analyze_reviewer_patterns(self, reviewer_name: str, months: int = 6) -> Dict:
        """Analyze patterns for a specific reviewer over the last N months.
        
        Args:
            reviewer_name: Name of the reviewer to analyze
            months: Number of months to look back
            
        Returns:
            Dictionary containing analysis results
        """
        since_date = datetime.now() - timedelta(days=months * 30)
        mrs = self.get_merge_requests(since_date)
        
        reviewer_comments = []
        all_comments = []
        
        print(f"Analyzing {len(mrs)} merge requests...")
        
        for mr in mrs:
            comments = self.get_mr_reviews(mr)
            all_comments.extend(comments)
            
            # Filter comments by the specific reviewer
            reviewer_comments.extend([
                comment for comment in comments 
                if comment.author.lower() == reviewer_name.lower()
            ])
        
        # Analyze reviewer patterns
        reviewer_stats = self._calculate_reviewer_stats(reviewer_comments)
        
        # Compare with team averages
        team_stats = self._calculate_team_stats(all_comments)
        
        return {
            'reviewer_stats': reviewer_stats,
            'team_stats': team_stats,
            'all_comments': all_comments,
            'reviewer_comments': reviewer_comments,
            'analysis_period': f"{months} months",
            'total_mrs_analyzed': len(mrs)
        }
    
    def _calculate_reviewer_stats(self, comments: List[ReviewComment]) -> ReviewerStats:
        """Calculate statistics for a specific reviewer.
        
        Args:
            comments: List of reviewer's comments
            
        Returns:
            ReviewerStats object
        """
        if not comments:
            return ReviewerStats(
                reviewer_name="Unknown",
                total_reviews=0,
                approved_count=0,
                requested_changes_count=0,
                comment_only_count=0,
                avg_sentiment_textblob=0.0,
                avg_sentiment_vader={},
                reviewed_authors={},
                sentiment_by_author={}
            )
        
        reviewer_name = comments[0].author
        total_reviews = len(comments)
        
        # Count approval statuses
        approved_count = sum(1 for c in comments if c.approval_status == 'approved')
        requested_changes_count = sum(1 for c in comments if c.approval_status == 'requested_changes')
        comment_only_count = sum(1 for c in comments if c.approval_status == 'commented')
        
        # Calculate average sentiments
        textblob_scores = [c.sentiment_textblob for c in comments]
        avg_sentiment_textblob = sum(textblob_scores) / len(textblob_scores) if textblob_scores else 0.0
        
        # Average VADER scores
        vader_keys = ['compound', 'pos', 'neu', 'neg']
        avg_sentiment_vader = {}
        for key in vader_keys:
            scores = [c.sentiment_vader.get(key, 0) for c in comments]
            avg_sentiment_vader[key] = sum(scores) / len(scores) if scores else 0.0
        
        # Count reviews by author
        reviewed_authors = defaultdict(int)
        sentiment_by_author = defaultdict(list)
        
        for comment in comments:
            reviewed_authors[comment.mr_author] += 1
            sentiment_by_author[comment.mr_author].append(comment.sentiment_textblob)
        
        return ReviewerStats(
            reviewer_name=reviewer_name,
            total_reviews=total_reviews,
            approved_count=approved_count,
            requested_changes_count=requested_changes_count,
            comment_only_count=comment_only_count,
            avg_sentiment_textblob=avg_sentiment_textblob,
            avg_sentiment_vader=avg_sentiment_vader,
            reviewed_authors=dict(reviewed_authors),
            sentiment_by_author=dict(sentiment_by_author)
        )
    
    def _calculate_team_stats(self, all_comments: List[ReviewComment]) -> Dict:
        """Calculate team-wide statistics for comparison.
        
        Args:
            all_comments: List of all comments from all reviewers
            
        Returns:
            Dictionary with team statistics
        """
        if not all_comments:
            return {}
        
        # Group by reviewer
        reviewer_groups = defaultdict(list)
        for comment in all_comments:
            reviewer_groups[comment.author].append(comment)
        
        team_stats = {}
        for reviewer, comments in reviewer_groups.items():
            stats = self._calculate_reviewer_stats(comments)
            team_stats[reviewer] = asdict(stats)
        
        return team_stats
    
    def analyze_team_patterns(self, months: int = 6) -> Dict:
        """Analyze patterns for the entire team over the last N months.
        
        Args:
            months: Number of months to look back
            
        Returns:
            Dictionary containing team analysis results
        """
        since_date = datetime.now() - timedelta(days=months * 30)
        mrs = self.get_merge_requests(since_date)
        
        all_comments = []
        
        print(f"Analyzing {len(mrs)} merge requests for team patterns...")
        
        for mr in mrs:
            comments = self.get_mr_reviews(mr)
            all_comments.extend(comments)
        
        # Calculate team statistics
        team_stats = self._calculate_team_stats(all_comments)
        
        # Calculate cross-team patterns
        team_patterns = self._analyze_cross_team_patterns(all_comments)
        
        return {
            'team_stats': team_stats,
            'team_patterns': team_patterns,
            'all_comments': all_comments,
            'analysis_period': f"{months} months",
            'total_mrs_analyzed': len(mrs),
            'reviewer_stats': None  # No specific reviewer for team analysis
        }
    
    def _analyze_cross_team_patterns(self, all_comments: List[ReviewComment]) -> Dict:
        """Analyze cross-team interaction patterns.
        
        Args:
            all_comments: List of all comments from all reviewers
            
        Returns:
            Dictionary with cross-team patterns
        """
        patterns = {
            'reviewer_to_author_matrix': defaultdict(lambda: defaultdict(list)),
            'most_active_reviewers': {},
            'most_reviewed_authors': {},
            'sentiment_patterns': {},
            'collaboration_network': {}
        }
        
        # Build reviewer-to-author matrix
        for comment in all_comments:
            patterns['reviewer_to_author_matrix'][comment.author][comment.mr_author].append(comment.sentiment_textblob)
        
        # Calculate most active reviewers
        reviewer_counts = defaultdict(int)
        for comment in all_comments:
            reviewer_counts[comment.author] += 1
        patterns['most_active_reviewers'] = dict(sorted(reviewer_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Calculate most reviewed authors
        author_counts = defaultdict(int)
        for comment in all_comments:
            author_counts[comment.mr_author] += 1
        patterns['most_reviewed_authors'] = dict(sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Calculate sentiment patterns
        for reviewer, authors in patterns['reviewer_to_author_matrix'].items():
            patterns['sentiment_patterns'][reviewer] = {}
            for author, sentiments in authors.items():
                if sentiments:
                    patterns['sentiment_patterns'][reviewer][author] = {
                        'avg_sentiment': sum(sentiments) / len(sentiments),
                        'review_count': len(sentiments),
                        'sentiment_std': (sum((s - sum(sentiments)/len(sentiments))**2 for s in sentiments) / len(sentiments))**0.5
                    }
        
        return patterns

    def enhance_with_llm(self, comments: List[ReviewComment], model: str = "llama3.2") -> List[Dict]:
        """Use Ollama LLM to provide additional insights on comments.
        
        Args:
            comments: List of comments to analyze
            model: Ollama model to use
            
        Returns:
            List of enhanced comment analyses
        """
        enhanced_comments = []
        
        try:
            for comment in comments[:10]:  # Limit to first 10 for demo
                prompt = f"""
                Analyze this code review comment for tone, professionalism, and potential bias:
                
                Comment: "{comment.body}"
                Author: {comment.author}
                MR Author: {comment.mr_author}
                
                Provide a brief analysis of:
                1. Tone (professional, harsh, supportive, etc.)
                2. Constructiveness (helpful suggestions vs just criticism)
                3. Potential bias indicators
                4. Overall sentiment
                
                Keep response concise (2-3 sentences max).
                """
                
                response = ollama.chat(
                    model=model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                
                enhanced_comments.append({
                    'comment': asdict(comment),
                    'llm_analysis': response['message']['content']
                })
                
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            # Return original comments without LLM enhancement
            enhanced_comments = [{'comment': asdict(c), 'llm_analysis': 'LLM analysis unavailable'} for c in comments]
        
        return enhanced_comments
