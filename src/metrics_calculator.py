"""
Core metrics calculation logic for GitLab review analysis.
"""
import statistics
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime, timedelta

try:
    # Try relative imports first (when used as package)
    from .models import DeveloperMetrics, ProjectMetrics, ReviewComment
except ImportError:
    # Fall back to absolute imports (when used directly)
    from models import DeveloperMetrics, ProjectMetrics, ReviewComment


class MetricsCalculator:
    """Calculates various metrics for GitLab review analysis."""
    
    def __init__(self):
        self.metrics_cache = {}
    
    def calculate_developer_metrics(self, developer_name: str, comments: List[ReviewComment], 
                                  mrs_data: List[Dict]) -> DeveloperMetrics:
        """Calculate comprehensive metrics for a developer."""
        
        # Basic MR statistics
        dev_mrs = [mr for mr in mrs_data if mr.get('author', {}).get('name') == developer_name]
        
        total_mrs = len(dev_mrs)
        merged_mrs = len([mr for mr in dev_mrs if mr.get('state') == 'merged'])
        closed_mrs = len([mr for mr in dev_mrs if mr.get('state') == 'closed'])
        
        # Review time calculations
        review_times = []
        merge_times = []
        
        for mr in dev_mrs:
            created_at = mr.get('created_at')
            merged_at = mr.get('merged_at')
            updated_at = mr.get('updated_at')
            
            if created_at and updated_at:
                # Calculate time from creation to last update (review time)
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if isinstance(updated_at, str):
                    updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                
                review_time = (updated_at - created_at).total_seconds() / 3600  # hours
                review_times.append(review_time)
            
            if created_at and merged_at:
                # Calculate time from creation to merge
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if isinstance(merged_at, str):
                    merged_at = datetime.fromisoformat(merged_at.replace('Z', '+00:00'))
                
                merge_time = (merged_at - created_at).total_seconds() / 3600  # hours
                merge_times.append(merge_time)
        
        avg_review_time = statistics.mean(review_times) if review_times else 0
        avg_merge_time = statistics.mean(merge_times) if merge_times else 0
        
        # Comment analysis
        dev_comments = [c for c in comments if c.author == developer_name]
        received_comments = [c for c in comments if c.mr_author == developer_name]
        
        comments_made = len(dev_comments)
        comments_received = len(received_comments)
        
        # Approval analysis
        approvals_given = len([c for c in dev_comments if c.approval_status == 'approved'])
        approvals_received = len([c for c in received_comments if c.approval_status == 'approved'])
        
        change_requests_made = len([c for c in dev_comments if c.approval_status == 'requested_changes'])
        change_requests_received = len([c for c in received_comments if c.approval_status == 'requested_changes'])
        
        # Code contribution metrics (would need to be extracted from MR data)
        lines_added = sum([mr.get('changes_count', 0) for mr in dev_mrs])
        lines_removed = 0  # Would need specific API data
        commits = sum([len(mr.get('commits', [])) for mr in dev_mrs])
        
        # Calculate negative behavior metrics
        negative_sentiment_comments = [c for c in dev_comments if c.sentiment_textblob < -0.2]
        negative_comments_ratio = len(negative_sentiment_comments) / max(comments_made, 1)
        
        # Excessive commenting (more than 10 comments per MR on average)
        if total_mrs > 0:
            avg_comments_per_mr = comments_made / total_mrs
            excessive_comments_ratio = 1.0 if avg_comments_per_mr > 10 else avg_comments_per_mr / 10
        else:
            excessive_comments_ratio = 0.0
        
        # Blocking MRs ratio
        total_reviews = approvals_given + change_requests_made
        blocking_mrs_ratio = change_requests_made / max(total_reviews, 1)
        
        # Average time to approve (would need timestamp analysis)
        avg_time_to_approve = 24.0  # Placeholder - would need actual calculation
        
        # Rejection rate
        rejection_rate = change_requests_made / max(total_reviews, 1)
        
        return DeveloperMetrics(
            name=developer_name,
            total_mrs=total_mrs,
            merged_mrs=merged_mrs,
            closed_mrs=closed_mrs,
            avg_review_time=avg_review_time,
            avg_merge_time=avg_merge_time,
            comments_made=comments_made,
            comments_received=comments_received,
            approvals_given=approvals_given,
            approvals_received=approvals_received,
            change_requests_made=change_requests_made,
            change_requests_received=change_requests_received,
            lines_added=lines_added,
            lines_removed=lines_removed,
            commits=commits,
            negative_comments_ratio=negative_comments_ratio,
            excessive_comments_ratio=excessive_comments_ratio,
            blocking_mrs_ratio=blocking_mrs_ratio,
            avg_time_to_approve=avg_time_to_approve,
            rejection_rate=rejection_rate
        )
    
    def calculate_project_metrics(self, all_comments: List[ReviewComment], 
                                mrs_data: List[Dict]) -> ProjectMetrics:
        """Calculate overall project metrics."""
        
        total_mrs = len(mrs_data)
        total_commits = sum([len(mr.get('commits', [])) for mr in mrs_data])
        
        # Get unique developers
        developers = set()
        for comment in all_comments:
            developers.add(comment.author)
            developers.add(comment.mr_author)
        total_developers = len(developers)
        
        # Calculate average review and merge times
        review_times = []
        merge_times = []
        
        for mr in mrs_data:
            created_at = mr.get('created_at')
            merged_at = mr.get('merged_at')
            updated_at = mr.get('updated_at')
            
            if created_at and updated_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if isinstance(updated_at, str):
                    updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                
                review_time = (updated_at - created_at).total_seconds() / 3600
                review_times.append(review_time)
            
            if created_at and merged_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if isinstance(merged_at, str):
                    merged_at = datetime.fromisoformat(merged_at.replace('Z', '+00:00'))
                
                merge_time = (merged_at - created_at).total_seconds() / 3600
                merge_times.append(merge_time)
        
        avg_review_time = statistics.mean(review_times) if review_times else 0
        avg_merge_time = statistics.mean(merge_times) if merge_times else 0
        
        # Calculate collaboration score based on comment distribution
        collaboration_score = self._calculate_collaboration_score(all_comments)
        
        # Calculate code quality score based on review patterns
        code_quality_score = self._calculate_code_quality_score(all_comments, mrs_data)
        
        return ProjectMetrics(
            total_mrs=total_mrs,
            total_commits=total_commits,
            total_developers=total_developers,
            avg_review_time=avg_review_time,
            avg_merge_time=avg_merge_time,
            collaboration_score=collaboration_score,
            code_quality_score=code_quality_score
        )
    
    def _calculate_collaboration_score(self, comments: List[ReviewComment]) -> float:
        """Calculate collaboration score based on review participation."""
        if not comments:
            return 0.0
        
        # Count interactions between different people
        interactions = defaultdict(set)
        for comment in comments:
            interactions[comment.author].add(comment.mr_author)
            interactions[comment.mr_author].add(comment.author)
        
        # Calculate average number of people each person interacts with
        if not interactions:
            return 0.0
        
        interaction_counts = [len(people) for people in interactions.values()]
        avg_interactions = statistics.mean(interaction_counts)
        
        # Normalize to 0-100 scale (assuming max 10 interactions is excellent)
        collaboration_score = min(100, (avg_interactions / 10) * 100)
        
        return collaboration_score
    
    def _calculate_code_quality_score(self, comments: List[ReviewComment], 
                                    mrs_data: List[Dict]) -> float:
        """Calculate code quality score based on review patterns."""
        if not comments or not mrs_data:
            return 50.0  # Neutral score
        
        # Count constructive comments vs total comments
        constructive_comments = 0
        total_comments = len(comments)
        
        constructive_keywords = ['suggest', 'recommend', 'consider', 'improve', 'better']
        
        for comment in comments:
            body_lower = comment.body.lower()
            if any(keyword in body_lower for keyword in constructive_keywords):
                constructive_comments += 1
        
        constructive_ratio = constructive_comments / max(total_comments, 1)
        
        # Count MRs that required changes vs total MRs
        mrs_with_changes = len([mr for mr in mrs_data if any(
            c.mr_title == mr.get('title', '') and c.approval_status == 'requested_changes'
            for c in comments
        )])
        
        change_ratio = mrs_with_changes / max(len(mrs_data), 1)
        
        # Calculate quality score
        # High constructive ratio and moderate change ratio indicate good quality process
        quality_score = (constructive_ratio * 50) + ((1 - min(change_ratio, 0.8)) * 50)
        
        return min(100, max(0, quality_score))
    
    def calculate_sentiment_statistics(self, comments: List[ReviewComment]) -> Dict[str, float]:
        """Calculate comprehensive sentiment statistics."""
        if not comments:
            return {
                'mean': 0.0,
                'median': 0.0,
                'std_dev': 0.0,
                'min': 0.0,
                'max': 0.0,
                'positive_ratio': 0.0,
                'negative_ratio': 0.0,
                'neutral_ratio': 0.0
            }
        
        sentiments = [comment.sentiment_textblob for comment in comments]
        
        mean_sentiment = statistics.mean(sentiments)
        median_sentiment = statistics.median(sentiments)
        std_dev = statistics.stdev(sentiments) if len(sentiments) > 1 else 0.0
        min_sentiment = min(sentiments)
        max_sentiment = max(sentiments)
        
        # Calculate ratios
        positive_count = sum(1 for s in sentiments if s > 0.1)
        negative_count = sum(1 for s in sentiments if s < -0.1)
        neutral_count = len(sentiments) - positive_count - negative_count
        
        total = len(sentiments)
        positive_ratio = positive_count / total
        negative_ratio = negative_count / total
        neutral_ratio = neutral_count / total
        
        return {
            'mean': mean_sentiment,
            'median': median_sentiment,
            'std_dev': std_dev,
            'min': min_sentiment,
            'max': max_sentiment,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'neutral_ratio': neutral_ratio
        }
    
    def calculate_reviewer_consistency(self, comments: List[ReviewComment]) -> Dict[str, float]:
        """Calculate consistency metrics for reviewers."""
        reviewer_sentiments = defaultdict(list)
        reviewer_approval_rates = defaultdict(lambda: {'approved': 0, 'changes': 0, 'comments': 0})
        
        for comment in comments:
            reviewer = comment.author
            reviewer_sentiments[reviewer].append(comment.sentiment_textblob)
            reviewer_approval_rates[reviewer][comment.approval_status] += 1
        
        consistency_scores = {}
        
        for reviewer, sentiments in reviewer_sentiments.items():
            if len(sentiments) < 3:  # Need minimum data for consistency analysis
                consistency_scores[reviewer] = 50.0  # Neutral score
                continue
            
            # Calculate sentiment consistency (lower std dev = more consistent)
            sentiment_std = statistics.stdev(sentiments)
            sentiment_consistency = max(0, 100 - (sentiment_std * 100))
            
            # Calculate approval pattern consistency
            approvals = reviewer_approval_rates[reviewer]
            total_reviews = sum(approvals.values())
            
            if total_reviews > 0:
                approval_rate = approvals['approved'] / total_reviews
                change_rate = approvals['changes'] / total_reviews
                
                # Consistent reviewers have moderate approval rates (not too high or low)
                optimal_approval_rate = 0.6  # 60% approval rate is considered balanced
                approval_consistency = 100 - abs(approval_rate - optimal_approval_rate) * 100
            else:
                approval_consistency = 50.0
            
            # Combine scores
            consistency_scores[reviewer] = (sentiment_consistency + approval_consistency) / 2
        
        return consistency_scores
    
    def calculate_bias_indicators(self, comments: List[ReviewComment]) -> Dict[str, Any]:
        """Calculate potential bias indicators."""
        author_sentiments = defaultdict(list)
        author_approval_rates = defaultdict(lambda: {'approved': 0, 'changes': 0, 'comments': 0})
        
        # Group by MR author (who is being reviewed)
        for comment in comments:
            mr_author = comment.mr_author
            author_sentiments[mr_author].append(comment.sentiment_textblob)
            author_approval_rates[mr_author][comment.approval_status] += 1
        
        bias_indicators = {
            'sentiment_variance': {},
            'approval_rate_variance': {},
            'potential_bias_targets': [],
            'overall_bias_score': 0.0
        }
        
        # Calculate sentiment variance for each author
        all_sentiments = []
        for author, sentiments in author_sentiments.items():
            if len(sentiments) >= 3:  # Minimum data requirement
                author_mean = statistics.mean(sentiments)
                author_std = statistics.stdev(sentiments) if len(sentiments) > 1 else 0
                
                bias_indicators['sentiment_variance'][author] = {
                    'mean': author_mean,
                    'std_dev': author_std,
                    'sample_size': len(sentiments)
                }
                
                all_sentiments.extend(sentiments)
                
                # Flag potential bias targets (consistently negative treatment)
                if author_mean < -0.3 and len(sentiments) >= 5:
                    bias_indicators['potential_bias_targets'].append({
                        'author': author,
                        'mean_sentiment': author_mean,
                        'review_count': len(sentiments)
                    })
        
        # Calculate approval rate variance
        for author, approvals in author_approval_rates.items():
            total = sum(approvals.values())
            if total >= 3:
                approval_rate = approvals['approved'] / total
                change_rate = approvals['changes'] / total
                
                bias_indicators['approval_rate_variance'][author] = {
                    'approval_rate': approval_rate,
                    'change_request_rate': change_rate,
                    'total_reviews': total
                }
        
        # Calculate overall bias score
        if len(author_sentiments) > 1:
            author_means = [
                statistics.mean(sentiments) 
                for sentiments in author_sentiments.values() 
                if len(sentiments) >= 3
            ]
            
            if len(author_means) > 1:
                # High variance in mean sentiments across authors indicates potential bias
                sentiment_variance = statistics.stdev(author_means)
                bias_indicators['overall_bias_score'] = min(100, sentiment_variance * 100)
        
        return bias_indicators
    
    def calculate_temporal_trends(self, comments: List[ReviewComment]) -> Dict[str, Any]:
        """Calculate trends over time."""
        if not comments:
            return {'monthly_trends': {}, 'weekly_patterns': {}, 'daily_patterns': {}}
        
        # Sort comments by date
        sorted_comments = sorted(comments, key=lambda x: x.created_at)
        
        # Monthly trends
        monthly_data = defaultdict(lambda: {'sentiments': [], 'count': 0})
        for comment in sorted_comments:
            month_key = comment.created_at.strftime('%Y-%m')
            monthly_data[month_key]['sentiments'].append(comment.sentiment_textblob)
            monthly_data[month_key]['count'] += 1
        
        monthly_trends = {}
        for month, data in monthly_data.items():
            monthly_trends[month] = {
                'avg_sentiment': statistics.mean(data['sentiments']),
                'comment_count': data['count'],
                'sentiment_std': statistics.stdev(data['sentiments']) if len(data['sentiments']) > 1 else 0
            }
        
        # Weekly patterns (day of week)
        weekly_data = defaultdict(lambda: {'sentiments': [], 'count': 0})
        for comment in sorted_comments:
            day_name = comment.created_at.strftime('%A')
            weekly_data[day_name]['sentiments'].append(comment.sentiment_textblob)
            weekly_data[day_name]['count'] += 1
        
        weekly_patterns = {}
        for day, data in weekly_data.items():
            weekly_patterns[day] = {
                'avg_sentiment': statistics.mean(data['sentiments']),
                'comment_count': data['count']
            }
        
        # Daily patterns (hour of day)
        daily_data = defaultdict(lambda: {'sentiments': [], 'count': 0})
        for comment in sorted_comments:
            hour = comment.created_at.hour
            daily_data[hour]['sentiments'].append(comment.sentiment_textblob)
            daily_data[hour]['count'] += 1
        
        daily_patterns = {}
        for hour, data in daily_data.items():
            daily_patterns[hour] = {
                'avg_sentiment': statistics.mean(data['sentiments']),
                'comment_count': data['count']
            }
        
        return {
            'monthly_trends': monthly_trends,
            'weekly_patterns': weekly_patterns,
            'daily_patterns': daily_patterns
        }
