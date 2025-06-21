"""
Data models and classes for GitLab analysis reporting.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class DeveloperMetrics:
    """Metrics for a single developer."""
    name: str
    total_mrs: int
    merged_mrs: int
    closed_mrs: int
    avg_review_time: float
    avg_merge_time: float
    comments_made: int
    comments_received: int
    approvals_given: int
    approvals_received: int
    change_requests_made: int
    change_requests_received: int
    lines_added: int
    lines_removed: int
    commits: int
    
    # Negative behavior metrics
    negative_comments_ratio: float = 0.0
    excessive_comments_ratio: float = 0.0
    blocking_mrs_ratio: float = 0.0
    avg_time_to_approve: float = 0.0
    rejection_rate: float = 0.0


@dataclass
class ProjectMetrics:
    """Overall project metrics."""
    total_mrs: int
    total_commits: int
    total_developers: int
    avg_review_time: float
    avg_merge_time: float
    collaboration_score: float
    code_quality_score: float
    
    
@dataclass
class BehaviorPattern:
    """Represents a negative behavior pattern."""
    pattern_type: str
    severity: str  # 'low', 'medium', 'high'
    description: str
    frequency: int
    impact_score: float
    examples: List[str]
    recommendations: List[str]


@dataclass
class DeveloperBehaviorAnalysis:
    """Comprehensive behavior analysis for a developer."""
    developer_name: str
    overall_behavior_score: float  # 0-100, higher is better
    negative_patterns: List[BehaviorPattern]
    positive_patterns: List[str]
    collaboration_style: str
    communication_tone: str
    review_quality: str
    improvement_areas: List[str]
    strengths: List[str]


@dataclass
class ReviewComment:
    """Represents a review comment with enhanced analysis."""
    author: str
    mr_author: str
    mr_title: str
    body: str
    sentiment_textblob: float
    approval_status: str
    created_at: datetime
    
    # Enhanced fields for behavior analysis
    toxicity_score: float = 0.0
    constructiveness_score: float = 0.0
    urgency_level: str = "low"
    contains_suggestions: bool = False
    contains_praise: bool = False
    contains_criticism: bool = False
    word_count: int = 0
