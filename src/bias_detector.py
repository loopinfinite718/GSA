"""
Bias detection module for GitLab review analysis.

This module provides advanced algorithms for detecting bias patterns in code reviews,
identifying negative behavior, and generating actionable recommendations.
"""

import statistics
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Any, Set, Optional

from data_models import (
    ReviewComment, BehaviorPattern, DeveloperTreatment, 
    BiasRiskLevel, SeverityLevel, BiasAnalysis
)


class BiasDetector:
    """Detects bias patterns in code review behavior."""
    
    def __init__(self):
        """Initialize the bias detector with default thresholds."""
        # Thresholds for bias detection
        self.sentiment_variance_threshold = 0.4  # High variance between developers
        self.negative_sentiment_threshold = -0.2  # Consistently negative sentiment
        self.high_rejection_threshold = 0.6  # High rejection rate
        self.excessive_comment_threshold = 15  # Excessive comments per MR
        
        # Patterns for detecting toxic language
        self.negative_keywords = [
            'terrible', 'awful', 'horrible', 'stupid', 'dumb', 'ridiculous',
            'waste', 'nonsense', 'garbage', 'trash', 'pathetic', 'useless',
            'incompetent', 'lazy', 'sloppy', 'unprofessional', 'horrible',
            'disgusting', 'idiotic', 'moronic', 'shameful'
        ]
        
        self.toxic_patterns = [
            r'\bbad\b.*\bcode\b', r'\bwrong\b.*\bway\b', r'\bhate\b.*\bthis\b',
            r'\bterrible\b.*\bimplementation\b', r'\bwhat.*\bwrong.*\byou\b'
        ]
        
        self.constructive_keywords = [
            'suggest', 'recommend', 'consider', 'try', 'maybe', 'could',
            'would', 'perhaps', 'how about', 'what if', 'alternative'
        ]
    
    def analyze_developer_treatment(self, all_comments: List[ReviewComment]) -> Dict[str, DeveloperTreatment]:
        """Analyze how each developer is treated by different reviewers.
        
        Args:
            all_comments: List of all review comments
            
        Returns:
            Dictionary mapping developer names to their treatment analysis
        """
        developer_analysis = {}
        
        # Group comments by MR author (developer)
        comments_by_developer = defaultdict(list)
        for comment in all_comments:
            comments_by_developer[comment.mr_author].append(comment)
        
        for developer, dev_comments in comments_by_developer.items():
            analysis = self._analyze_individual_developer_treatment(developer, dev_comments)
            developer_analysis[developer] = analysis
        
        return developer_analysis
    
    def _analyze_individual_developer_treatment(self, developer: str, 
                                              comments: List[ReviewComment]) -> DeveloperTreatment:
        """Analyze treatment patterns for a specific developer.
        
        Args:
            developer: Developer name
            comments: List of comments directed at the developer's MRs
            
        Returns:
            DeveloperTreatment object with analysis results
        """
        # Group by reviewer
        reviewer_sentiments = defaultdict(list)
        reviewer_actions = defaultdict(lambda: {'approved': 0, 'requested_changes': 0, 'commented': 0})
        reviewer_toxicity = defaultdict(list)
        reviewer_blocking_behavior = defaultdict(list)
        
        for comment in comments:
            reviewer = comment.author
            reviewer_sentiments[reviewer].append(comment.sentiment.textblob_score)
            reviewer_actions[reviewer][comment.approval_status.value] += 1
            
            # Calculate toxicity score for this comment
            toxicity_score = self._calculate_toxicity_score(comment.body)
            reviewer_toxicity[reviewer].append(toxicity_score)
            
            # Track blocking behavior patterns
            if comment.approval_status.value == 'requested_changes':
                reviewer_blocking_behavior[reviewer].append({
                    'reason': self._extract_blocking_reason(comment.body),
                    'severity': self._assess_blocking_severity(comment.body),
                    'constructiveness': self._assess_constructiveness(comment.body),
                    'comment': comment
                })
        
        # Calculate reviewer statistics
        reviewer_stats = {}
        for reviewer, sentiments in reviewer_sentiments.items():
            avg_sentiment = sum(sentiments) / len(sentiments)
            avg_toxicity = sum(reviewer_toxicity[reviewer]) / len(reviewer_toxicity[reviewer])
            actions = reviewer_actions[reviewer]
            total_reviews = sum(actions.values())
            
            # Analyze blocking behavior
            blocking_analysis = self._analyze_blocking_patterns(reviewer_blocking_behavior[reviewer])
            
            # Determine treatment level with enhanced criteria
            treatment_info = self._determine_treatment_level(
                avg_sentiment, avg_toxicity, actions, total_reviews, blocking_analysis
            )
            
            # Identify negative patterns
            negative_patterns = self._identify_negative_patterns(reviewer, comments)
            
            # Find negative comments for documentation
            negative_comments = [
                comment for comment in comments 
                if comment.author == reviewer and comment.sentiment.textblob_score < self.negative_sentiment_threshold
            ]
            
            reviewer_stats[reviewer] = {
                'avg_sentiment': avg_sentiment,
                'avg_toxicity': avg_toxicity,
                'review_count': len(sentiments),
                'treatment': treatment_info['level'],
                'treatment_color': treatment_info['color'],
                'treatment_icon': treatment_info['icon'],
                'approval_rate': actions['approved'] / total_reviews if total_reviews > 0 else 0,
                'change_request_rate': actions['requested_changes'] / total_reviews if total_reviews > 0 else 0,
                'blocking_analysis': blocking_analysis,
                'negative_patterns': negative_patterns,
                'communication_style': self._determine_communication_style(sentiments, reviewer_toxicity[reviewer]),
                'negative_comments': self._document_negative_behavior(negative_comments)
            }
        
        # Overall analysis for the developer
        all_sentiments = [comment.sentiment.textblob_score for comment in comments]
        overall_sentiment = sum(all_sentiments) / len(all_sentiments) if all_sentiments else 0
        
        # Find most and least supportive reviewers
        if reviewer_stats:
            most_supportive = max(reviewer_stats.items(), key=lambda x: x[1]['avg_sentiment'])
            least_supportive = min(reviewer_stats.items(), key=lambda x: x[1]['avg_sentiment'])
            sentiment_range = most_supportive[1]['avg_sentiment'] - least_supportive[1]['avg_sentiment']
            
            # Determine bias indicators
            bias_indicators = []
            if overall_sentiment < self.negative_sentiment_threshold:
                bias_indicators.append("Receives generally negative feedback across the team")
            if sentiment_range > self.sentiment_variance_threshold + 0.2:  # Higher threshold for cross-reviewer variance
                bias_indicators.append("Very inconsistent treatment from different reviewers")
            
            critical_reviewers = [r for r, stats in reviewer_stats.items() 
                                if stats['treatment'] in ['Critical', 'Very Critical', 'Potentially Toxic']]
            if len(critical_reviewers) > len(reviewer_stats) * 0.5:
                bias_indicators.append("Majority of reviewers are critical")
            
            # Check for potential targeting
            high_toxicity_reviewers = [r for r, stats in reviewer_stats.items() if stats['avg_toxicity'] > 0.5]
            if high_toxicity_reviewers:
                bias_indicators.append(f"Potentially toxic behavior from: {', '.join(high_toxicity_reviewers)}")
            
            # Calculate bias risk
            bias_risk = BiasRiskLevel.HIGH if len(bias_indicators) >= 3 else \
                        BiasRiskLevel.MEDIUM if len(bias_indicators) >= 2 else \
                        BiasRiskLevel.LOW
            
            # Generate recommendations
            recommendations = self._generate_developer_recommendations(bias_indicators, reviewer_stats)
            
            return DeveloperTreatment(
                developer_name=developer,
                overall_sentiment=overall_sentiment,
                total_reviews=len(comments),
                total_negative_reviews=sum(1 for c in comments if c.sentiment.textblob_score < self.negative_sentiment_threshold),
                sentiment_range=sentiment_range,
                bias_indicators=bias_indicators,
                bias_risk=bias_risk,
                recommendations=recommendations,
                reviewer_stats=reviewer_stats
            )
        
        # Default return if no reviewer stats
        return DeveloperTreatment(
            developer_name=developer,
            overall_sentiment=overall_sentiment,
            total_reviews=len(comments),
            total_negative_reviews=0,
            sentiment_range=0.0,
            bias_indicators=[],
            bias_risk=BiasRiskLevel.LOW,
            recommendations=["Insufficient data for analysis"],
            reviewer_stats={}
        )
    
    def _calculate_toxicity_score(self, text: str) -> float:
        """Calculate toxicity score for a comment (0-1).
        
        Args:
            text: Comment text
            
        Returns:
            Toxicity score between 0 and 1
        """
        text_lower = text.lower()
        toxicity_score = 0.0
        
        # Check for negative keywords
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
        toxicity_score += negative_count * 0.2
        
        # Check for toxic patterns
        import re
        pattern_matches = sum(1 for pattern in self.toxic_patterns if re.search(pattern, text_lower))
        toxicity_score += pattern_matches * 0.3
        
        # Check for personal attacks
        personal_attacks = ['you are', 'you\'re', 'your fault', 'you did', 'you made']
        personal_attack_count = sum(1 for attack in personal_attacks if attack in text_lower)
        toxicity_score += personal_attack_count * 0.25
        
        # Check for constructive language (reduces toxicity)
        constructive_count = sum(1 for keyword in self.constructive_keywords if keyword in text_lower)
        toxicity_score -= constructive_count * 0.1
        
        return max(0.0, min(1.0, toxicity_score))
    
    def _extract_blocking_reason(self, comment_body: str) -> str:
        """Extract the main reason for blocking an MR.
        
        Args:
            comment_body: Comment text
            
        Returns:
            Category of blocking reason
        """
        reasons = {
            'code_quality': ['quality', 'standards', 'clean', 'refactor', 'design'],
            'testing': ['test', 'coverage', 'unit test', 'integration'],
            'documentation': ['docs', 'documentation', 'comment', 'readme'],
            'security': ['security', 'vulnerability', 'auth', 'permission'],
            'performance': ['performance', 'slow', 'optimization', 'memory'],
            'style': ['style', 'formatting', 'lint', 'convention'],
            'unclear': ['unclear', 'confusing', 'understand', 'explain']
        }
        
        comment_lower = comment_body.lower()
        for reason, keywords in reasons.items():
            if any(keyword in comment_lower for keyword in keywords):
                return reason
        
        return 'other'
    
    def _assess_blocking_severity(self, comment_body: str) -> str:
        """Assess the severity of a blocking comment.
        
        Args:
            comment_body: Comment text
            
        Returns:
            Severity level (high, medium, low)
        """
        high_severity_words = ['critical', 'major', 'blocking', 'must', 'required', 'urgent']
        medium_severity_words = ['should', 'important', 'needed', 'consider']
        
        comment_lower = comment_body.lower()
        
        if any(word in comment_lower for word in high_severity_words):
            return 'high'
        elif any(word in comment_lower for word in medium_severity_words):
            return 'medium'
        else:
            return 'low'
    
    def _assess_constructiveness(self, text: str) -> int:
        """Assess constructiveness of a comment (0-100).
        
        Args:
            text: Comment text
            
        Returns:
            Constructiveness score (0-100)
        """
        constructive_indicators = ['suggest', 'recommend', 'consider', 'try', 'how about', 'maybe', 'could']
        destructive_indicators = ['bad', 'terrible', 'wrong', 'stupid', 'awful']
        solution_indicators = ['here is', 'you can', 'try this', 'example', 'documentation']
        
        text_lower = text.lower()
        score = 50  # Base score
        
        # Add points for constructive language
        score += sum(5 for word in constructive_indicators if word in text_lower)
        score += sum(10 for word in solution_indicators if word in text_lower)
        
        # Subtract points for destructive language
        score -= sum(10 for word in destructive_indicators if word in text_lower)
        
        # Bonus for providing examples or links
        if 'http' in text_lower or 'example' in text_lower:
            score += 15
        
        return max(0, min(100, score))
    
    def _analyze_blocking_patterns(self, blocking_behaviors: List[Dict]) -> Dict:
        """Analyze patterns in blocking behavior.
        
        Args:
            blocking_behaviors: List of blocking behavior data
            
        Returns:
            Dictionary with blocking pattern analysis
        """
        if not blocking_behaviors:
            return {'frequency': 0, 'patterns': [], 'severity_distribution': {}}
        
        reasons = [b['reason'] for b in blocking_behaviors]
        severities = [b['severity'] for b in blocking_behaviors]
        constructiveness_scores = [b['constructiveness'] for b in blocking_behaviors]
        
        patterns = []
        if len(set(reasons)) == 1 and len(reasons) > 2:
            patterns.append(f"Consistently blocks for {reasons[0]} issues")
        
        if len([s for s in severities if s == 'high']) > len(severities) * 0.6:
            patterns.append("Tends to escalate issues to high severity")
        
        avg_constructiveness = sum(constructiveness_scores) / len(constructiveness_scores)
        if avg_constructiveness < 40:
            patterns.append("Blocking comments lack constructive feedback")
        
        return {
            'frequency': len(blocking_behaviors),
            'patterns': patterns,
            'severity_distribution': dict(Counter(severities)),
            'avg_constructiveness': avg_constructiveness,
            'common_reasons': dict(Counter(reasons))
        }
    
    def _determine_treatment_level(self, avg_sentiment: float, avg_toxicity: float, 
                                 actions: Dict, total_reviews: int, 
                                 blocking_analysis: Dict) -> Dict:
        """Determine treatment level with enhanced criteria.
        
        Args:
            avg_sentiment: Average sentiment score
            avg_toxicity: Average toxicity score
            actions: Dictionary of approval actions
            total_reviews: Total number of reviews
            blocking_analysis: Blocking behavior analysis
            
        Returns:
            Dictionary with treatment level information
        """
        # Calculate composite score
        sentiment_score = avg_sentiment
        toxicity_penalty = -avg_toxicity * 0.5
        blocking_penalty = 0
        
        if blocking_analysis['frequency'] > 0:
            change_request_rate = actions['requested_changes'] / total_reviews if total_reviews > 0 else 0
            if change_request_rate > 0.7:
                blocking_penalty -= 0.3
            elif blocking_analysis['avg_constructiveness'] < 40:
                blocking_penalty -= 0.2
        
        composite_score = sentiment_score + toxicity_penalty + blocking_penalty
        
        # Determine treatment level
        if composite_score >= 0.3:
            return {'level': 'Very Supportive', 'color': '#27ae60', 'icon': '🤗'}
        elif composite_score >= 0.1:
            return {'level': 'Supportive', 'color': '#2ecc71', 'icon': '😊'}
        elif composite_score >= -0.1:
            return {'level': 'Neutral', 'color': '#95a5a6', 'icon': '😐'}
        elif composite_score >= -0.3:
            return {'level': 'Critical', 'color': '#f39c12', 'icon': '🤨'}
        elif composite_score >= -0.5:
            return {'level': 'Very Critical', 'color': '#e67e22', 'icon': '😠'}
        else:
            return {'level': 'Potentially Toxic', 'color': '#e74c3c', 'icon': '🚨'}
    
    def _identify_negative_patterns(self, reviewer: str, comments: List[ReviewComment]) -> List[str]:
        """Identify specific negative patterns in reviewer behavior.
        
        Args:
            reviewer: Reviewer name
            comments: List of comments
            
        Returns:
            List of identified negative patterns
        """
        patterns = []
        reviewer_comments = [c for c in comments if c.author == reviewer]
        
        if not reviewer_comments:
            return patterns
        
        # Check for excessive commenting
        comment_counts_per_mr = defaultdict(int)
        for comment in reviewer_comments:
            comment_counts_per_mr[comment.mr_title] += 1
        
        excessive_mrs = [count for count in comment_counts_per_mr.values() 
                        if count > self.excessive_comment_threshold]
        if len(excessive_mrs) > len(comment_counts_per_mr) * 0.3:
            patterns.append("Tends to over-comment on merge requests")
        
        # Check for consistently negative sentiment
        sentiments = [c.sentiment.textblob_score for c in reviewer_comments]
        avg_sentiment = sum(sentiments) / len(sentiments)
        if avg_sentiment < -0.3:
            patterns.append("Consistently negative sentiment in reviews")
        
        # Check for nitpicking behavior
        short_critical_comments = [
            comment for comment in reviewer_comments 
            if len(comment.body) < 50 and comment.sentiment.textblob_score < -0.2
        ]
        if len(short_critical_comments) > len(reviewer_comments) * 0.4:
            patterns.append("Shows nitpicking behavior with short critical comments")
        
        # Check for blocking without constructive feedback
        change_requests = [c for c in reviewer_comments if c.approval_status.value == 'requested_changes']
        if change_requests:
            constructive_keywords = ['suggest', 'recommend', 'consider', 'try', 'example']
            non_constructive = [c for c in change_requests 
                              if not any(keyword in c.body.lower() for keyword in constructive_keywords)]
            if len(non_constructive) > len(change_requests) * 0.5:
                patterns.append("Blocks MRs without providing constructive feedback")
        
        return patterns
    
    def _determine_communication_style(self, sentiments: List[float], toxicity_scores: List[float]) -> str:
        """Determine overall communication style based on sentiment and toxicity.
        
        Args:
            sentiments: List of sentiment scores
            toxicity_scores: List of toxicity scores
            
        Returns:
            Communication style description
        """
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        avg_toxicity = sum(toxicity_scores) / len(toxicity_scores) if toxicity_scores else 0
        
        if avg_sentiment > 0.2 and avg_toxicity < 0.2:
            return "Encouraging & Constructive"
        elif avg_sentiment > 0.0 and avg_toxicity < 0.3:
            return "Professional & Balanced"
        elif avg_sentiment > -0.2 and avg_toxicity < 0.4:
            return "Direct & Factual"
        elif avg_sentiment > -0.4 and avg_toxicity < 0.6:
            return "Critical & Demanding"
        else:
            return "Harsh & Potentially Problematic"
    
    def _document_negative_behavior(self, comments: List[ReviewComment]) -> List[Dict]:
        """Document instances of negative behavior with context.
        
        Args:
            comments: List of negative comments
            
        Returns:
            List of documented negative behavior instances
        """
        documented_instances = []
        
        for comment in comments:
            toxicity_score = self._calculate_toxicity_score(comment.body)
            constructiveness_score = self._assess_constructiveness(comment.body)
            
            # Categorize the negative behavior
            categories = []
            if toxicity_score > 0.5:
                categories.append("Toxic language")
            if "you" in comment.body.lower() and comment.sentiment.textblob_score < -0.3:
                categories.append("Personal criticism")
            if constructiveness_score < 30:
                categories.append("Non-constructive feedback")
            if len(comment.body) < 50 and comment.sentiment.textblob_score < -0.3:
                categories.append("Dismissive comment")
            
            # Default category if none detected
            if not categories:
                categories.append("Negative sentiment")
            
            documented_instances.append({
                'comment': comment,
                'toxicity_score': toxicity_score,
                'constructiveness_score': constructiveness_score,
                'categories': categories,
                'severity': 'high' if toxicity_score > 0.7 else 'medium' if toxicity_score > 0.4 else 'low',
                'context': {
                    'mr_title': comment.mr_title,
                    'created_at': comment.created_at.isoformat(),
                    'mr_author': comment.mr_author
                }
            })
        
        # Sort by toxicity score (most toxic first)
        return sorted(documented_instances, key=lambda x: x['toxicity_score'], reverse=True)
    
    def _generate_developer_recommendations(self, bias_indicators: List[str], 
                                          reviewer_stats: Dict) -> List[str]:
        """Generate recommendations for improving developer treatment.
        
        Args:
            bias_indicators: List of bias indicators
            reviewer_stats: Dictionary of reviewer statistics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if len(bias_indicators) >= 2:
            recommendations.append("🚨 Consider investigating potential bias or harassment")
            recommendations.append("📋 Implement structured review guidelines to ensure fairness")
        
        # Check for toxic reviewers
        toxic_reviewers = [name for name, stats in reviewer_stats.items() 
                         if stats['treatment'] == 'Potentially Toxic']
        if toxic_reviewers:
            recommendations.append(f"⚠️ Address toxic behavior from: {', '.join(toxic_reviewers)}")
        
        # Check for inconsistent treatment
        sentiment_range = max([stats['avg_sentiment'] for stats in reviewer_stats.values()]) - \
                         min([stats['avg_sentiment'] for stats in reviewer_stats.values()])
        if sentiment_range > 0.6:
            recommendations.append("📊 Work on standardizing review feedback across the team")
        
        # Check for excessive blocking
        high_blockers = [name for name, stats in reviewer_stats.items() 
                        if stats['change_request_rate'] > 0.7]
        if high_blockers:
            recommendations.append(f"🔄 Review blocking patterns for: {', '.join(high_blockers)}")
        
        if not recommendations:
            recommendations.append("✅ Treatment appears fair and balanced")
        
        return recommendations
    
    def calculate_bias_indicators(self, all_comments: List[ReviewComment]) -> BiasAnalysis:
        """Calculate comprehensive bias indicators across the team.
        
        Args:
            all_comments: List of all review comments
            
        Returns:
            BiasAnalysis object with detailed bias analysis
        """
        author_sentiments = defaultdict(list)
        author_approval_rates = defaultdict(lambda: {'approved': 0, 'requested_changes': 0, 'commented': 0})
        
        # Group by MR author (who is being reviewed)
        for comment in all_comments:
            mr_author = comment.mr_author
            author_sentiments[mr_author].append(comment.sentiment.textblob_score)
            author_approval_rates[mr_author][comment.approval_status.value] += 1
        
        # Calculate sentiment variance for each author
        sentiment_variance = {}
        for author, sentiments in author_sentiments.items():
            if len(sentiments) >= 3:  # Minimum data requirement
                author_mean = statistics.mean(sentiments)
                author_std = statistics.stdev(sentiments) if len(sentiments) > 1 else 0
                
                sentiment_variance[author] = {
                    'mean': author_mean,
                    'std_dev': author_std,
                    'sample_size': len(sentiments)
                }
        
        # Identify potential bias targets
        potential_bias_targets = []
        for author, variance_data in sentiment_variance.items():
            if variance_data['mean'] < self.negative_sentiment_threshold and variance_data['sample_size'] >= 5:
                potential_bias_targets.append({
                    'author': author,
                    'mean_sentiment': variance_data['mean'],
                    'review_count': variance_data['sample_size']
                })
        
        # Calculate overall bias score
        overall_bias_score = 0.0
        if len(author_sentiments) > 1:
            author_means = [
                statistics.mean(sentiments) 
                for sentiments in author_sentiments.values() 
                if len(sentiments) >= 3
            ]
            
            if len(author_means) > 1:
                # High variance in mean sentiments across authors indicates potential bias
                sentiment_variance_value = statistics.stdev(author_means)
                overall_bias_score = min(100, sentiment_variance_value * 100)
        
        # Determine overall risk level
        overall_risk = BiasRiskLevel.HIGH if overall_bias_score > 70 or len(potential_bias_targets) > 0 else \
                      BiasRiskLevel.MEDIUM if overall_bias_score > 40 or len(potential_bias_targets) > 0 else \
                      BiasRiskLevel.LOW
        
        # Generate specific risks
        specific_risks = []
        for target in potential_bias_targets:
            specific_risks.append(f"High bias risk detected for {target['author']}")
        
        # Generate author analysis
        author_analysis = {}
        for author, variance_data in sentiment_variance.items():
            risk_level = BiasRiskLevel.HIGH if variance_data['mean'] < -0.3 else \
                        BiasRiskLevel.MEDIUM if variance_data['mean'] < -0.1 else \
                        BiasRiskLevel.LOW
            
            patterns = []
            if variance_data['mean'] < -0.3:
                patterns.append("Consistently negative sentiment")
            elif variance_data['mean'] < -0.1:
                patterns.append("Tendency towards negative feedback")
            
            author_analysis[author] = {
                'avg_sentiment': variance_data['mean'],
                'review_count': variance_data['sample_size'],
                'sentiment_std': variance_data['std_dev'],
                'risk_level': risk_level,
                'patterns': patterns
            }
        
        # Generate mitigation strategies
        mitigation_strategies = []
        if overall_risk in [BiasRiskLevel.MEDIUM, BiasRiskLevel.HIGH]:
            mitigation_strategies = [
                "Implement anonymous code review processes",
                "Use structured review templates and checklists",
                "Provide bias awareness training for reviewers",
                "Monitor review patterns regularly",
                "Establish clear review guidelines and standards"
            ]
        
        return BiasAnalysis(
            overall_risk=overall_risk,
            specific_risks=specific_risks,
            author_analysis=author_analysis,
            mitigation_strategies=mitigation_strategies,
            sentiment_variance=sentiment_variance
        )