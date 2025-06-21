"""
Core data models for the GitLab Review Analyzer.

This module defines the fundamental data structures used throughout the application,
following a domain-driven design approach to clearly represent the core concepts
of GitLab merge request reviews and sentiment analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Union, Any
from enum import Enum


class ApprovalStatus(Enum):
    """Enumeration of possible merge request approval statuses."""
    APPROVED = "approved"
    REQUESTED_CHANGES = "requested_changes"
    COMMENTED = "commented"


class SeverityLevel(Enum):
    """Enumeration of severity levels for behavior patterns."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BiasRiskLevel(Enum):
    """Enumeration of bias risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class SentimentScore:
    """Represents sentiment analysis scores from multiple algorithms."""
    textblob_score: float
    vader_compound: float
    vader_positive: float
    vader_neutral: float
    vader_negative: float
    
    @property
    def is_negative(self) -> bool:
        """Check if the sentiment is predominantly negative."""
        return self.textblob_score < -0.2 or self.vader_compound < -0.2
    
    @property
    def is_positive(self) -> bool:
        """Check if the sentiment is predominantly positive."""
        return self.textblob_score > 0.2 and self.vader_compound > 0.2
    
    @property
    def is_neutral(self) -> bool:
        """Check if the sentiment is predominantly neutral."""
        return not self.is_negative and not self.is_positive


@dataclass
class ReviewComment:
    """Represents a single review comment with enhanced analysis."""
    # Core properties
    id: str
    author: str
    body: str
    created_at: datetime
    mr_id: int
    mr_title: str
    mr_author: str
    approval_status: ApprovalStatus
    
    # Sentiment analysis
    sentiment: SentimentScore
    
    # Enhanced analysis
    toxicity_score: float = 0.0
    constructiveness_score: float = 0.0
    urgency_level: str = "low"
    contains_suggestions: bool = False
    contains_praise: bool = False
    contains_criticism: bool = False
    word_count: int = 0
    
    def __post_init__(self):
        """Initialize derived properties after initialization."""
        if isinstance(self.approval_status, str):
            self.approval_status = ApprovalStatus(self.approval_status)
        
        if self.word_count == 0:
            self.word_count = len(self.body.split())


@dataclass
class BehaviorPattern:
    """Represents a detected behavior pattern in reviews."""
    pattern_type: str
    severity: SeverityLevel
    description: str
    frequency: int
    impact_score: float
    examples: List[str]
    recommendations: List[str]
    
    def __post_init__(self):
        """Initialize derived properties after initialization."""
        if isinstance(self.severity, str):
            self.severity = SeverityLevel(self.severity)


@dataclass
class ReviewerStats:
    """Statistics and metrics for a specific reviewer."""
    reviewer_name: str
    total_reviews: int
    approved_count: int
    requested_changes_count: int
    comment_only_count: int
    avg_sentiment_textblob: float
    avg_sentiment_vader: Dict[str, float]
    reviewed_authors: Dict[str, int]
    sentiment_by_author: Dict[str, List[float]]
    
    # Enhanced metrics
    negative_comments_ratio: float = 0.0
    excessive_comments_ratio: float = 0.0
    blocking_mrs_ratio: float = 0.0
    avg_time_to_approve: float = 0.0
    rejection_rate: float = 0.0
    
    @property
    def approval_rate(self) -> float:
        """Calculate the approval rate."""
        return self.approved_count / max(self.total_reviews, 1)
    
    @property
    def change_request_rate(self) -> float:
        """Calculate the change request rate."""
        return self.requested_changes_count / max(self.total_reviews, 1)


@dataclass
class DeveloperTreatment:
    """Analysis of how a developer is treated by reviewers."""
    developer_name: str
    overall_sentiment: float
    total_reviews: int
    total_negative_reviews: int
    sentiment_range: float
    bias_indicators: List[str]
    bias_risk: BiasRiskLevel
    recommendations: List[str]
    reviewer_stats: Dict[str, Dict[str, Any]]
    
    def __post_init__(self):
        """Initialize derived properties after initialization."""
        if isinstance(self.bias_risk, str):
            self.bias_risk = BiasRiskLevel(self.bias_risk)


@dataclass
class ProjectMetrics:
    """Overall project metrics and statistics."""
    total_mrs: int
    total_commits: int
    total_developers: int
    avg_review_time: float
    avg_merge_time: float
    collaboration_score: float
    code_quality_score: float
    
    # Team dynamics metrics
    team_cohesion: float = 0.0
    communication_balance: float = 0.0
    review_distribution: Dict[str, float] = field(default_factory=dict)


@dataclass
class BiasAnalysis:
    """Comprehensive bias analysis results."""
    overall_risk: BiasRiskLevel
    specific_risks: List[str]
    author_analysis: Dict[str, Dict[str, Any]]
    mitigation_strategies: List[str]
    sentiment_variance: Dict[str, Dict[str, float]]
    
    def __post_init__(self):
        """Initialize derived properties after initialization."""
        if isinstance(self.overall_risk, str):
            self.overall_risk = BiasRiskLevel(self.overall_risk)


@dataclass
class AnalysisResult:
    """Complete analysis result containing all components."""
    reviewer_stats: Optional[ReviewerStats] = None
    team_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    reviewer_comments: List[ReviewComment] = field(default_factory=list)
    all_comments: List[ReviewComment] = field(default_factory=list)
    analysis_period: str = "N/A"
    total_mrs_analyzed: int = 0
    
    # Enhanced analysis components
    developer_treatment: Dict[str, DeveloperTreatment] = field(default_factory=dict)
    project_metrics: Optional[ProjectMetrics] = None
    bias_analysis: Optional[BiasAnalysis] = None
    temporal_trends: Dict[str, Any] = field(default_factory=dict)