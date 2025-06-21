#!/usr/bin/env python3
"""
GitLab Review Sentiment Analysis Tool

Main script to analyze GitLab merge request reviews and generate sentiment analysis reports.
This tool helps identify potential bias patterns in code reviews by analyzing sentiment
towards different team members and documenting instances of negative behavior.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from data_models import AnalysisResult
from gitlab_client import GitLabClient
from sentiment_analyzer import SentimentAnalyzer, LLMAnalyzer
from bias_detector import BiasDetector
from report_generator import ReportGenerator


def load_config() -> Dict[str, str]:
    """Load configuration from environment variables or .env file."""
    config = {}
    
    # Try to load from .env file if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Load required configuration
    config['gitlab_url'] = os.getenv('GITLAB_URL')
    config['gitlab_token'] = os.getenv('GITLAB_TOKEN')
    config['project_id'] = os.getenv('GITLAB_PROJECT_ID')
    
    # Validate required config
    missing_config = []
    for key, value in config.items():
        if not value:
            missing_config.append(key.upper())
    
    if missing_config:
        print("❌ Missing required configuration:")
        for key in missing_config:
            print(f"   - {key}")
        print("\nPlease set these environment variables or create a .env file.")
        print("Example .env file:")
        print("GITLAB_URL=https://gitlab.example.com")
        print("GITLAB_TOKEN=your_personal_access_token")
        print("GITLAB_PROJECT_ID=123")
        sys.exit(1)
    
    return config


def run_analysis(args: argparse.Namespace, config: Dict[str, str]) -> AnalysisResult:
    """Run the GitLab review analysis.
    
    Args:
        args: Command-line arguments
        config: Configuration dictionary
        
    Returns:
        AnalysisResult object with analysis results
    """
    # Initialize components
    gitlab_client = GitLabClient(
        gitlab_url=config['gitlab_url'],
        private_token=config['gitlab_token'],
        project_id=config['project_id']
    )
    
    sentiment_analyzer = SentimentAnalyzer()
    bias_detector = BiasDetector()
    
    # Set up LLM analyzer if requested
    if args.use_llm:
        try:
            llm_analyzer = LLMAnalyzer(model=args.llm_model)
            sentiment_analyzer.set_llm_analyzer(llm_analyzer)
            print("🤖 LLM enhancement enabled")
        except Exception as e:
            print(f"⚠️  LLM initialization failed: {e}")
            print("   Continuing without LLM enhancement")
    
    # Calculate analysis period
    since_date = datetime.now() - timedelta(days=args.months * 30)
    
    # Create analysis result object
    analysis_result = AnalysisResult(
        analysis_period=f"{args.months} months",
    )
    
    print(f"\n🏃‍♂️ Running analysis for period: {args.months} months...")
    
    # Get merge requests
    print("📥 Fetching merge requests...")
    mrs = gitlab_client.get_merge_requests(since_date)
    analysis_result.total_mrs_analyzed = len(mrs)
    print(f"   Found {len(mrs)} merge requests")
    
    # Process merge requests
    print("🔍 Analyzing merge request reviews...")
    all_comments = []
    
    for mr in mrs:
        # Get reviews for this MR
        mr_comments = gitlab_client.get_mr_reviews(mr, sentiment_analyzer)
        all_comments.extend(mr_comments)
    
    analysis_result.all_comments = all_comments
    print(f"   Processed {len(all_comments)} review comments")
    
    # Team-wide analysis
    if args.team_report:
        print("📊 Generating team-wide analysis...")
        # Analyze developer treatment
        developer_treatments = bias_detector.analyze_developer_treatment(all_comments)
        analysis_result.developer_treatment = developer_treatments
        
        # Calculate bias indicators
        bias_analysis = bias_detector.calculate_bias_indicators(all_comments)
        analysis_result.bias_analysis = bias_analysis
        
        print(f"   Analyzed {len(developer_treatments)} developers")
    
    # Individual reviewer analysis
    else:
        print(f"📊 Analyzing reviewer: {args.reviewer_name}")
        # Filter comments by reviewer
        reviewer_comments = [c for c in all_comments if c.author.lower() == args.reviewer_name.lower()]
        
        if not reviewer_comments:
            print(f"⚠️  No comments found for reviewer '{args.reviewer_name}'")
            print("   - Check if the name is correct (case-sensitive)")
            print("   - Verify the reviewer has made comments in the specified period")
            return None
        
        analysis_result.reviewer_comments = reviewer_comments
        
        # Calculate reviewer statistics
        from gitlab_analyzer import ReviewerStats  # Import here to avoid circular imports
        
        # Group by MR author
        sentiment_by_author = {}
        reviewed_authors = {}
        
        for comment in reviewer_comments:
            author = comment.mr_author
            if author not in sentiment_by_author:
                sentiment_by_author[author] = []
                reviewed_authors[author] = 0
            sentiment_by_author[author].append(comment.sentiment.textblob_score)
            reviewed_authors[author] += 1
        
        # Calculate overall stats
        total_reviews = len(reviewer_comments)
        approved_count = sum(1 for c in reviewer_comments if c.approval_status.value == 'approved')
        requested_changes_count = sum(1 for c in reviewer_comments if c.approval_status.value == 'requested_changes')
        comment_only_count = sum(1 for c in reviewer_comments if c.approval_status.value == 'commented')
        
        all_sentiments = [c.sentiment.textblob_score for c in reviewer_comments]
        avg_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0
        
        # Calculate average VADER scores
        vader_scores = {"compound": 0.0, "pos": 0.0, "neu": 0.0, "neg": 0.0}
        for comment in reviewer_comments:
            vader_scores["compound"] += comment.sentiment.vader_compound
            vader_scores["pos"] += comment.sentiment.vader_positive
            vader_scores["neu"] += comment.sentiment.vader_neutral
            vader_scores["neg"] += comment.sentiment.vader_negative
        
        for key in vader_scores:
            vader_scores[key] /= len(reviewer_comments) if reviewer_comments else 1
        
        reviewer_stats = ReviewerStats(
            reviewer_name=args.reviewer_name,
            total_reviews=total_reviews,
            approved_count=approved_count,
            requested_changes_count=requested_changes_count,
            comment_only_count=comment_only_count,
            avg_sentiment_textblob=avg_sentiment,
            avg_sentiment_vader=vader_scores,
            reviewed_authors=reviewed_authors,
            sentiment_by_author=sentiment_by_author
        )
        
        analysis_result.reviewer_stats = reviewer_stats
        
        # Also run developer treatment analysis for comparison
        developer_treatments = bias_detector.analyze_developer_treatment(all_comments)
        analysis_result.developer_treatment = developer_treatments
        
        # Calculate bias indicators
        bias_analysis = bias_detector.calculate_bias_indicators(all_comments)
        analysis_result.bias_analysis = bias_analysis
        
        print(f"   Analyzed {len(reviewer_comments)} comments by {args.reviewer_name}")
    
    return analysis_result


def main() -> int:
    """Main function to run the GitLab review analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze GitLab merge request reviews for sentiment patterns and bias detection"
    )
    parser.add_argument(
        "reviewer_name",
        help="Name of the reviewer to analyze (or 'Team' for team-wide analysis)"
    )
    parser.add_argument(
        "--months",
        type=int,
        default=6,
        help="Number of months to analyze (default: 6)"
    )
    parser.add_argument(
        "--output",
        default="gitlab_review_analysis.html",
        help="Output HTML file path (default: gitlab_review_analysis.html)"
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use Ollama LLM for enhanced comment analysis"
    )
    parser.add_argument(
        "--llm-model",
        default="llama3.2",
        help="Ollama model to use (default: llama3.2)"
    )
    parser.add_argument(
        "--team-report",
        action="store_true",
        help="Generate a comprehensive team report instead of individual analysis"
    )
    
    args = parser.parse_args()
    
    print("🔍 GitLab Review Sentiment Analyzer")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    print(f"📊 {'Team-wide analysis' if args.team_report else f'Analyzing reviewer: {args.reviewer_name}'}")
    print(f"📅 Analysis period: {args.months} months")
    print(f"🎯 GitLab project: {config['project_id']}")
    
    try:
        # Run analysis
        analysis_result = run_analysis(args, config)
        
        if not analysis_result:
            return 1
        
        # Generate report
        print("📝 Generating HTML report...")
        report_generator = ReportGenerator()
        output_file = report_generator.generate_report(
            analysis_result=analysis_result,
            output_file=args.output
        )
        
        print(f"\n✅ Report generated: {output_file}")
        print(f"🌐 Open the file in your browser to view the detailed analysis")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        print("Please check your configuration and try again.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
