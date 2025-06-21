#!/usr/bin/env python3
"""
GitLab Reviewer Analysis Tool

This script analyzes a specific reviewer's behavior on GitLab merge requests:
1. Accepts one Reviewer name as input
2. Analyzes who they gave reviews to and counts "Request change" blocks
3. Calculates statistics per person (blocks, comments, avg comments, comment length)
4. Creates 2 CSV files:
   - Summary CSV: Rankings of who got blocked most, who got most comments, who got most approvals without comments
   - Detailed CSV: Complete record of each comment grouped by PR author
"""

import os
import sys
import argparse
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

# Add src to path to import project modules
sys.path.append(str(Path(__file__).parent / "src"))

from data_models import ReviewComment, ApprovalStatus, SentimentScore
from gitlab_client import GitLabClient
from sentiment_analyzer import SentimentAnalyzer


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


def analyze_reviewer(gitlab_client: GitLabClient, reviewer_name: str, months: int = 6) -> Dict[str, Any]:
    """Analyze a specific reviewer's behavior.
    
    Args:
        gitlab_client: GitLabClient instance for API interactions
        reviewer_name: Name of the reviewer to analyze
        months: Number of months to look back
        
    Returns:
        Dictionary with analysis results
    """
    # Calculate analysis period
    since_date = datetime.now() - timedelta(days=months * 30)
    
    print(f"\n🔍 Analyzing reviewer '{reviewer_name}' for the past {months} months...")
    
    # Get merge requests
    print("📥 Fetching merge requests...")
    mrs = gitlab_client.get_merge_requests(since_date)
    print(f"   Found {len(mrs)} merge requests")
    
    # Process merge requests
    print("🔍 Analyzing merge request reviews...")
    all_comments = []
    
    # Create sentiment analyzer for the GitLabClient
    sentiment_analyzer = SentimentAnalyzer()
    
    for mr in mrs:
        # Get reviews for this MR
        mr_comments = gitlab_client.get_mr_reviews(mr, sentiment_analyzer)
        all_comments.extend(mr_comments)
    
    # Filter comments by reviewer
    reviewer_comments = [c for c in all_comments if c.author.lower() == reviewer_name.lower()]
    
    if not reviewer_comments:
        print(f"⚠️  No comments found for reviewer '{reviewer_name}'")
        print("   - Check if the name is correct (case-sensitive)")
        print("   - Verify the reviewer has made comments in the specified period")
        return {}
    
    print(f"   Found {len(reviewer_comments)} comments by {reviewer_name}")
    
    # Group comments by MR author
    comments_by_author = defaultdict(list)
    for comment in reviewer_comments:
        comments_by_author[comment.mr_author].append(comment)
    
    # Calculate statistics per author
    author_stats = {}
    for author, author_comments in comments_by_author.items():
        # Count blocks (requested changes)
        blocks_count = sum(1 for c in author_comments if c.approval_status == ApprovalStatus.REQUESTED_CHANGES)
        
        # Count total comments
        total_comments = len(author_comments)
        
        # Calculate average comments per MR
        mr_ids = set(c.mr_id for c in author_comments)
        avg_comments_per_mr = total_comments / len(mr_ids) if mr_ids else 0
        
        # Calculate average comment length
        comment_lengths = [len(c.body) for c in author_comments]
        avg_comment_length = sum(comment_lengths) / len(comment_lengths) if comment_lengths else 0
        
        # Count approvals without comments
        approvals_without_comments = sum(1 for c in author_comments 
                                        if c.approval_status == ApprovalStatus.APPROVED and len(c.body.strip()) < 10)
        
        author_stats[author] = {
            'blocks_count': blocks_count,
            'total_comments': total_comments,
            'avg_comments_per_mr': avg_comments_per_mr,
            'avg_comment_length': avg_comment_length,
            'approvals_without_comments': approvals_without_comments,
            'comments': author_comments
        }
    
    return {
        'reviewer_name': reviewer_name,
        'analysis_period': f"{months} months",
        'total_mrs_analyzed': len(mrs),
        'author_stats': author_stats
    }


def generate_summary_csv(analysis_results: Dict[str, Any], output_file: str) -> None:
    """Generate a summary CSV with rankings.
    
    Args:
        analysis_results: Analysis results dictionary
        output_file: Path to output CSV file
    """
    if not analysis_results or 'author_stats' not in analysis_results:
        print("⚠️  No data available to generate summary CSV")
        return
    
    author_stats = analysis_results['author_stats']
    reviewer_name = analysis_results['reviewer_name']
    
    # Prepare data for CSV
    csv_data = []
    
    # Sort authors by different metrics
    blocked_most = sorted(author_stats.items(), 
                         key=lambda x: x[1]['blocks_count'], 
                         reverse=True)
    
    most_comments = sorted(author_stats.items(), 
                          key=lambda x: x[1]['total_comments'], 
                          reverse=True)
    
    most_approvals_without_comments = sorted(author_stats.items(), 
                                           key=lambda x: x[1]['approvals_without_comments'], 
                                           reverse=True)
    
    # Add data for each author
    for author, stats in author_stats.items():
        blocked_rank = next(i for i, (a, _) in enumerate(blocked_most, 1) if a == author)
        comments_rank = next(i for i, (a, _) in enumerate(most_comments, 1) if a == author)
        approvals_rank = next(i for i, (a, _) in enumerate(most_approvals_without_comments, 1) if a == author)
        
        csv_data.append({
            'Author': author,
            'Total Comments Received': stats['total_comments'],
            'Times Blocked': stats['blocks_count'],
            'Avg Comments Per MR': f"{stats['avg_comments_per_mr']:.2f}",
            'Avg Comment Length': f"{stats['avg_comment_length']:.2f}",
            'Approvals Without Comments': stats['approvals_without_comments'],
            'Blocked Rank': blocked_rank,
            'Comments Rank': comments_rank,
            'Silent Approvals Rank': approvals_rank
        })
    
    # Sort by blocked rank for the CSV
    csv_data.sort(key=lambda x: x['Blocked Rank'])
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Author', 'Total Comments Received', 'Times Blocked', 
                     'Avg Comments Per MR', 'Avg Comment Length', 
                     'Approvals Without Comments', 'Blocked Rank', 
                     'Comments Rank', 'Silent Approvals Rank']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"✅ Summary CSV generated: {output_file}")


def generate_detailed_csv(analysis_results: Dict[str, Any], output_file: str) -> None:
    """Generate a detailed CSV with all comments grouped by PR author.
    
    Args:
        analysis_results: Analysis results dictionary
        output_file: Path to output CSV file
    """
    if not analysis_results or 'author_stats' not in analysis_results:
        print("⚠️  No data available to generate detailed CSV")
        return
    
    author_stats = analysis_results['author_stats']
    reviewer_name = analysis_results['reviewer_name']
    
    # Prepare data for CSV
    csv_data = []
    
    for author, stats in author_stats.items():
        for comment in stats['comments']:
            csv_data.append({
                'Author': author,
                'MR ID': comment.mr_id,
                'MR Title': comment.mr_title,
                'Comment Date': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Approval Status': comment.approval_status.value,
                'Comment': comment.body,
                'Comment Length': len(comment.body),
                'Sentiment Score': f"{comment.sentiment.textblob_score:.2f}"
            })
    
    # Sort by author and date
    csv_data.sort(key=lambda x: (x['Author'], x['Comment Date']))
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Author', 'MR ID', 'MR Title', 'Comment Date', 
                     'Approval Status', 'Comment', 'Comment Length', 
                     'Sentiment Score']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"✅ Detailed CSV generated: {output_file}")


def main() -> int:
    """Main function to run the GitLab reviewer analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze a GitLab reviewer's behavior and generate CSV reports"
    )
    parser.add_argument(
        "reviewer_name",
        help="Name of the reviewer to analyze"
    )
    parser.add_argument(
        "--months",
        type=int,
        default=6,
        help="Number of months to analyze (default: 6)"
    )
    parser.add_argument(
        "--summary-csv",
        default="reviewer_summary.csv",
        help="Output path for summary CSV (default: reviewer_summary.csv)"
    )
    parser.add_argument(
        "--detailed-csv",
        default="reviewer_detailed.csv",
        help="Output path for detailed CSV (default: reviewer_detailed.csv)"
    )
    
    args = parser.parse_args()
    
    print("🔍 GitLab Reviewer Analysis Tool")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    print(f"📊 Analyzing reviewer: {args.reviewer_name}")
    print(f"📅 Analysis period: {args.months} months")
    print(f"🎯 GitLab project: {config['project_id']}")
    
    try:
        # Initialize GitLab client
        gitlab_client = GitLabClient(
            gitlab_url=config['gitlab_url'],
            private_token=config['gitlab_token'],
            project_id=config['project_id']
        )
        
        # Run analysis
        analysis_results = analyze_reviewer(
            gitlab_client=gitlab_client,
            reviewer_name=args.reviewer_name,
            months=args.months
        )
        
        if not analysis_results:
            return 1
        
        # Generate CSV files
        generate_summary_csv(analysis_results, args.summary_csv)
        generate_detailed_csv(analysis_results, args.detailed_csv)
        
        print("\n✅ Analysis complete!")
        print(f"📊 Summary CSV: {args.summary_csv}")
        print(f"📋 Detailed CSV: {args.detailed_csv}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        print("Please check your configuration and try again.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())