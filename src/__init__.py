"""
GitLab Analysis Package

This package provides comprehensive analysis tools for GitLab merge request reviews,
including sentiment analysis, bias detection, and developer behavior patterns.
"""

from .advanced_report_generator import AdvancedReportGenerator
from .report_generator import EnhancedReportGenerator
from .behavior_analyzer import BehaviorAnalyzer
from .metrics_calculator import MetricsCalculator
from .ui_components import UIComponentGenerator
from .models import (
    DeveloperMetrics,
    ProjectMetrics,
    BehaviorPattern,
    DeveloperBehaviorAnalysis,
    ReviewComment
)

__version__ = "2.0.0"
__author__ = "GitLab Analysis Team"

# Export main classes for easy import
__all__ = [
    'AdvancedReportGenerator',
    'EnhancedReportGenerator', 
    'BehaviorAnalyzer',
    'MetricsCalculator',
    'UIComponentGenerator',
    'DeveloperMetrics',
    'ProjectMetrics',
    'BehaviorPattern',
    'DeveloperBehaviorAnalysis',
    'ReviewComment'
]

# Backward compatibility
ReportGenerator = AdvancedReportGenerator  # For legacy code compatibility
