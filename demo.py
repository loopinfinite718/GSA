#!/usr/bin/env python3
"""
Demo script for GitLab Review Sentiment Analyzer

This script demonstrates the functionality of the GitLab Review Sentiment Analyzer
without requiring actual GitLab credentials. It creates sample data with simulated
bias patterns and generates a report.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from data_models import (
    ReviewComment, SentimentScore, ApprovalStatus, 
    AnalysisResult, BiasRiskLevel
)
from bias_detector import BiasDetector
from report_generator import ReportGenerator


def create_demo_data() -> AnalysisResult:
    """Create sample data with simulated bias patterns.
    
    Returns:
        AnalysisResult object with sample data
    """
    # Create sample comments
    all_comments = []
    
    # John Reviewer - Shows bias pattern towards Charlie
    john_comments = [
        # Positive towards Alice
        ReviewComment(
            id="1",
            author="John Reviewer",
            body="Excellent work on this feature! The implementation is clean and well-tested. Great job following the coding standards.",
            created_at=datetime.now() - timedelta(days=45),
            mr_id=1,
            mr_title="Add new authentication system",
            mr_author="Alice Developer",
            sentiment=SentimentScore(
                textblob_score=0.8,
                vader_compound=0.8,
                vader_positive=0.7,
                vader_neutral=0.2,
                vader_negative=0.1
            ),
            approval_status=ApprovalStatus.APPROVED
        ),
        ReviewComment(
            id="2",
            author="John Reviewer",
            body="LGTM! Nice use of design patterns here. Just a small suggestion: consider adding more error handling for edge cases.",
            created_at=datetime.now() - timedelta(days=40),
            mr_id=2,
            mr_title="Refactor user service",
            mr_author="Alice Developer",
            sentiment=SentimentScore(
                textblob_score=0.6,
                vader_compound=0.6,
                vader_positive=0.5,
                vader_neutral=0.4,
                vader_negative=0.1
            ),
            approval_status=ApprovalStatus.APPROVED
        ),
        
        # Neutral towards Bob
        ReviewComment(
            id="3",
            author="John Reviewer",
            body="The implementation works but could be improved. Consider using a more efficient algorithm for the sorting logic.",
            created_at=datetime.now() - timedelta(days=35),
            mr_id=4,
            mr_title="Optimize data processing",
            mr_author="Bob Developer",
            sentiment=SentimentScore(
                textblob_score=0.1,
                vader_compound=0.1,
                vader_positive=0.3,
                vader_neutral=0.5,
                vader_negative=0.2
            ),
            approval_status=ApprovalStatus.REQUESTED_CHANGES
        ),
        
        # Negative towards Charlie
        ReviewComment(
            id="4",
            author="John Reviewer",
            body="This code is a complete mess! The logic is convoluted and there are obvious bugs. This needs to be completely rewritten. I can't approve this in its current state.",
            created_at=datetime.now() - timedelta(days=38),
            mr_id=6,
            mr_title="Implement payment gateway",
            mr_author="Charlie Developer",
            sentiment=SentimentScore(
                textblob_score=-0.6,
                vader_compound=-0.7,
                vader_positive=0.0,
                vader_neutral=0.2,
                vader_negative=0.8
            ),
            approval_status=ApprovalStatus.REQUESTED_CHANGES
        ),
        ReviewComment(
            id="5",
            author="John Reviewer",
            body="Again with the poor error handling! How many times do I need to tell you to follow the team's coding standards? This is unacceptable.",
            created_at=datetime.now() - timedelta(days=28),
            mr_id=7,
            mr_title="Add input validation",
            mr_author="Charlie Developer",
            sentiment=SentimentScore(
                textblob_score=-0.5,
                vader_compound=-0.6,
                vader_positive=0.0,
                vader_neutral=0.3,
                vader_negative=0.7
            ),
            approval_status=ApprovalStatus.REQUESTED_CHANGES
        ),
    ]
    
    # Jane Reviewer - More balanced approach
    jane_comments = [
        ReviewComment(
            id="6",
            author="Jane Reviewer",
            body="Thanks for the contribution! I suggest extracting this logic into a separate utility function for better reusability.",
            created_at=datetime.now() - timedelta(days=42),
            mr_id=11,
            mr_title="Feature enhancement",
            mr_author="Alice Developer",
            sentiment=SentimentScore(
                textblob_score=0.5,
                vader_compound=0.5,
                vader_positive=0.4,
                vader_neutral=0.5,
                vader_negative=0.1
            ),
            approval_status=ApprovalStatus.APPROVED
        ),
        ReviewComment(
            id="7",
            author="Jane Reviewer",
            body="Good implementation! Consider using dependency injection here to make the code more testable.",
            created_at=datetime.now() - timedelta(days=32),
            mr_id=12,
            mr_title="Service layer refactoring",
            mr_author="Bob Developer",
            sentiment=SentimentScore(
                textblob_score=0.4,
                vader_compound=0.4,
                vader_positive=0.4,
                vader_neutral=0.5,
                vader_negative=0.1
            ),
            approval_status=ApprovalStatus.APPROVED
        ),
        ReviewComment(
            id="8",
            author="Jane Reviewer",
            body="I see some opportunities for improvement here. Let me suggest an alternative approach that might be more maintainable.",
            created_at=datetime.now() - timedelta(days=27),
            mr_id=13,
            mr_title="Database optimization",
            mr_author="Charlie Developer",
            sentiment=SentimentScore(
                textblob_score=0.2,
                vader_compound=0.2,
                vader_positive=0.3,
                vader_neutral=0.6,
                vader_negative=0.1
            ),
            approval_status=ApprovalStatus.COMMENTED
        ),
    ]
    
    # Mike Reviewer - Generally critical
    mike_comments = [
        ReviewComment(
            id="9",
            author="Mike Reviewer",
            body="This needs more work. The performance implications haven't been considered and the code is not following our style guide.",
            created_at=datetime.now() - timedelta(days=36),
            mr_id=14,
            mr_title="Performance optimization",
            mr_author="Alice Developer",
            sentiment=SentimentScore(
                textblob_score=-0.2,
                vader_compound=-0.3,
                vader_positive=0.1,
                vader_neutral=0.5,
                vader_negative=0.4
            ),
            approval_status=ApprovalStatus.REQUESTED_CHANGES
        ),
        ReviewComment(
            id="10",
            author="Mike Reviewer",
            body="Too many changes in one MR. Please split this into smaller, more focused pull requests.",
            created_at=datetime.now() - timedelta(days=29),
            mr_id=15,
            mr_title="Major refactoring",
            mr_author="Bob Developer",
            sentiment=SentimentScore(
                textblob_score=-0.1,
                vader_compound=-0.2,
                vader_positive=0.1,
                vader_neutral=0.6,
                vader_negative=0.3
            ),
            approval_status=ApprovalStatus.REQUESTED_CHANGES
        ),
    ]
    
    # Combine all comments
    all_comments.extend(john_comments)
    all_comments.extend(jane_comments)
    all_comments.extend(mike_comments)
    
    # Create analysis result
    analysis_result = AnalysisResult(
        analysis_period="6 months",
        total_mrs_analyzed=15,
        all_comments=all_comments,
        reviewer_comments=john_comments  # Focus on John for individual analysis
    )
    
    return analysis_result


def main():
    """Run the demo."""
    print("🚀 GitLab Review Sentiment Analyzer - Demo Mode")
    print("=" * 60)
    
    # Create demo data
    print("📊 Creating sample analysis data...")
    analysis_result = create_demo_data()
    
    # Run bias detection
    print("🔍 Running bias detection...")
    bias_detector = BiasDetector()
    
    # Analyze developer treatment
    developer_treatments = bias_detector.analyze_developer_treatment(analysis_result.all_comments)
    analysis_result.developer_treatment = developer_treatments
    
    # Calculate bias indicators
    bias_analysis = bias_detector.calculate_bias_indicators(analysis_result.all_comments)
    analysis_result.bias_analysis = bias_analysis
    
    # Generate report
    print("📝 Generating demo HTML report...")
    report_generator = ReportGenerator()
    output_file = report_generator.generate_report(
        analysis_result=analysis_result,
        output_file="demo_analysis.html"
    )
    
    print(f"\n✅ Demo report generated: {output_file}")
    print("🌐 Open the file in your browser to view the analysis")
    
    # Display summary of findings
    print("\n🚨 DEMO BIAS INDICATORS:")
    
    if bias_analysis.overall_risk == BiasRiskLevel.HIGH:
        print("   ⚠️  High bias risk detected")
    elif bias_analysis.overall_risk == BiasRiskLevel.MEDIUM:
        print("   ⚠️  Medium bias risk detected")
    
    for risk in bias_analysis.specific_risks:
        print(f"   ⚠️  {risk}")
    
    print("\n🎯 DEVELOPER TREATMENT:")
    for developer, treatment in developer_treatments.items():
        print(f"   {developer}: {treatment.bias_risk.value} risk, {treatment.total_negative_reviews} negative reviews")
        if treatment.bias_indicators:
            for indicator in treatment.bias_indicators:
                print(f"      - {indicator}")
    
    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    main()
