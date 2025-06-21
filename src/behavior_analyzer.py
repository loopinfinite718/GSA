"""
Advanced behavior analysis for identifying negative review patterns and developer treatment.
"""
import re
import statistics
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta

try:
    # Try relative imports first (when used as package)
    from .models import DeveloperMetrics, BehaviorPattern, DeveloperBehaviorAnalysis, ReviewComment
except ImportError:
    # Fall back to absolute imports (when used directly)
    from models import DeveloperMetrics, BehaviorPattern, DeveloperBehaviorAnalysis, ReviewComment


class BehaviorAnalyzer:
    """Analyzes developer behavior patterns for negative tendencies and bias detection."""
    
    def __init__(self):
        self.negative_comment_keywords = [
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
        
        self.praise_keywords = [
            'good', 'great', 'excellent', 'nice', 'well', 'perfect', 'awesome',
            'brilliant', 'clever', 'smart', 'elegant', 'clean', 'beautiful'
        ]
        
        # Thresholds for behavior pattern detection
        self.excessive_comment_threshold = 15  # comments per MR
        self.blocking_threshold = 0.3  # 30% of MRs with change requests
        self.negative_sentiment_threshold = -0.2
        self.toxicity_threshold = 0.7
        
    def analyze_developer_treatment(self, all_comments: List) -> Dict:
        """Analyze how each developer is treated by different reviewers."""
        developer_analysis = {}
        
        # Group comments by MR author (developer)
        comments_by_developer = defaultdict(list)
        for comment in all_comments:
            comments_by_developer[comment.mr_author].append(comment)
        
        for developer, dev_comments in comments_by_developer.items():
            analysis = self._analyze_individual_developer_treatment(developer, dev_comments)
            developer_analysis[developer] = analysis
        
        return developer_analysis
    
    def _analyze_individual_developer_treatment(self, developer: str, comments: List) -> Dict:
        """Analyze treatment patterns for a specific developer."""
        # Group by reviewer
        reviewer_sentiments = defaultdict(list)
        reviewer_actions = defaultdict(lambda: {'approved': 0, 'requested_changes': 0, 'commented': 0})
        reviewer_toxicity = defaultdict(list)
        reviewer_blocking_behavior = defaultdict(list)
        
        for comment in comments:
            reviewer = comment.author
            reviewer_sentiments[reviewer].append(comment.sentiment_textblob)
            reviewer_actions[reviewer][comment.approval_status] += 1
            reviewer_toxicity[reviewer].append(self._calculate_toxicity_score(comment.body))
            
            # Track blocking behavior patterns
            if comment.approval_status == 'requested_changes':
                reviewer_blocking_behavior[reviewer].append({
                    'reason': self._extract_blocking_reason(comment.body),
                    'severity': self._assess_blocking_severity(comment.body),
                    'constructiveness': self._assess_constructiveness(comment.body)
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
                'negative_patterns': self._identify_negative_patterns(reviewer, comments),
                'communication_style': self._determine_communication_style(sentiments, reviewer_toxicity[reviewer])
            }
        
        # Overall analysis for the developer
        return self._compile_developer_analysis(developer, comments, reviewer_stats)
    
    def _calculate_toxicity_score(self, text: str) -> float:
        """Calculate toxicity score for a comment (0-1)."""
        text_lower = text.lower()
        toxicity_score = 0.0
        
        # Check for negative keywords
        negative_count = sum(1 for keyword in self.negative_comment_keywords if keyword in text_lower)
        toxicity_score += negative_count * 0.2
        
        # Check for toxic patterns
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
        """Extract the main reason for blocking an MR."""
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
        """Assess the severity of a blocking comment."""
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
        """Assess constructiveness of a comment (0-100)."""
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
        """Analyze patterns in blocking behavior."""
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
                                 actions: Dict, total_reviews: int, blocking_analysis: Dict) -> Dict:
        """Determine treatment level with enhanced criteria."""
        
        # Calculate composite score
        sentiment_score = avg_sentiment
        toxicity_penalty = -avg_toxicity * 0.5
        blocking_penalty = 0
        
        if blocking_analysis['frequency'] > 0:
            change_request_rate = actions['requested_changes'] / total_reviews
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
    
    def _identify_negative_patterns(self, reviewer: str, comments: List) -> List[str]:
        """Identify specific negative patterns in reviewer behavior."""
        patterns = []
        
        # Analyze comment sentiments
        sentiments = [comment.sentiment_textblob for comment in comments]
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        if avg_sentiment < -0.3:
            patterns.append("Consistently negative sentiment in reviews")
        
        # Check for excessive commenting
        comment_counts_per_mr = defaultdict(int)
        for comment in comments:
            comment_counts_per_mr[comment.mr_title] += 1
        
        excessive_comment_mrs = [count for count in comment_counts_per_mr.values() 
                               if count > self.excessive_comment_threshold]
        if len(excessive_comment_mrs) > len(comment_counts_per_mr) * 0.3:
            patterns.append("Tends to over-comment on merge requests")
        
        # Check for nitpicking behavior
        short_critical_comments = [
            comment for comment in comments 
            if len(comment.body) < 50 and comment.sentiment_textblob < -0.2
        ]
        if len(short_critical_comments) > len(comments) * 0.4:
            patterns.append("Shows nitpicking behavior with short critical comments")
        
        # Check for blocking behavior without constructive feedback
        change_requests = [comment for comment in comments if comment.approval_status == 'requested_changes']
        low_constructiveness_blocks = [
            comment for comment in change_requests 
            if self._assess_constructiveness(comment.body) < 40
        ]
        if len(low_constructiveness_blocks) > len(change_requests) * 0.5:
            patterns.append("Blocks MRs without providing constructive feedback")
        
        return patterns
    
    def _determine_communication_style(self, sentiments: List[float], toxicity_scores: List[float]) -> str:
        """Determine overall communication style."""
        avg_sentiment = sum(sentiments) / len(sentiments)
        avg_toxicity = sum(toxicity_scores) / len(toxicity_scores)
        
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
    
    def _compile_developer_analysis(self, developer: str, comments: List, reviewer_stats: Dict) -> Dict:
        """Compile comprehensive analysis for a developer."""
        all_sentiments = [comment.sentiment_textblob for comment in comments]
        overall_sentiment = sum(all_sentiments) / len(all_sentiments)
        
        # Find most and least supportive reviewers
        if reviewer_stats:
            most_supportive = max(reviewer_stats.items(), key=lambda x: x[1]['avg_sentiment'])
            least_supportive = min(reviewer_stats.items(), key=lambda x: x[1]['avg_sentiment'])
            sentiment_range = most_supportive[1]['avg_sentiment'] - least_supportive[1]['avg_sentiment']
            
            # Determine bias indicators
            bias_indicators = []
            if overall_sentiment < -0.2:
                bias_indicators.append("Receives generally negative feedback across the team")
            if sentiment_range > 0.6:
                bias_indicators.append("Very inconsistent treatment from different reviewers")
            
            critical_reviewers = [r for r in reviewer_stats.values() 
                                if r['treatment'] in ['Critical', 'Very Critical', 'Potentially Toxic']]
            if len(critical_reviewers) > len(reviewer_stats) * 0.5:
                bias_indicators.append("Majority of reviewers are critical")
            
            # Check for potential targeting
            high_toxicity_reviewers = [r for r in reviewer_stats.values() if r['avg_toxicity'] > 0.5]
            if len(high_toxicity_reviewers) > 0:
                bias_indicators.append("Some reviewers show toxic behavior patterns")
            
            # Calculate bias risk
            bias_risk = 'high' if len(bias_indicators) >= 3 else 'medium' if len(bias_indicators) >= 2 else 'low'
            
            return {
                'reviewer_stats': reviewer_stats,
                'overall_sentiment': overall_sentiment,
                'total_reviews': len(comments),
                'most_supportive_reviewer': most_supportive[0],
                'least_supportive_reviewer': least_supportive[0],
                'sentiment_range': sentiment_range,
                'bias_indicators': bias_indicators,
                'bias_risk': bias_risk,
                'treatment_summary': self._generate_treatment_summary(reviewer_stats),
                'recommendations': self._generate_developer_recommendations(bias_indicators, reviewer_stats)
            }
        
        return {}
    
    def _generate_treatment_summary(self, reviewer_stats: Dict) -> Dict:
        """Generate a summary of how the developer is treated."""
        treatment_counts = Counter([stats['treatment'] for stats in reviewer_stats.values()])
        total_reviewers = len(reviewer_stats)
        
        return {
            'treatment_distribution': dict(treatment_counts),
            'dominant_treatment': treatment_counts.most_common(1)[0][0] if treatment_counts else 'Unknown',
            'support_ratio': (treatment_counts.get('Very Supportive', 0) + 
                            treatment_counts.get('Supportive', 0)) / total_reviewers,
            'critical_ratio': (treatment_counts.get('Critical', 0) + 
                             treatment_counts.get('Very Critical', 0) + 
                             treatment_counts.get('Potentially Toxic', 0)) / total_reviewers
        }
    
    def _generate_developer_recommendations(self, bias_indicators: List[str], reviewer_stats: Dict) -> List[str]:
        """Generate recommendations for improving developer treatment."""
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
