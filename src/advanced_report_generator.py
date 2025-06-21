"""
Advanced HTML Report Generator for GitLab Review Analysis

This module provides a compatibility layer for the new modular structure
while maintaining backward compatibility with existing code.
"""

try:
    # Try relative imports first (when used as package)
    from .report_generator import EnhancedReportGenerator
    from .behavior_analyzer import BehaviorAnalyzer
    from .metrics_calculator import MetricsCalculator
    from .ui_components import UIComponentGenerator
except ImportError:
    # Fall back to absolute imports (when used directly)
    try:
        from report_generator import EnhancedReportGenerator
        from behavior_analyzer import BehaviorAnalyzer
        from metrics_calculator import MetricsCalculator
        from ui_components import UIComponentGenerator
    except ImportError:
        # If modular components aren't available, use simplified fallback
        EnhancedReportGenerator = None
        BehaviorAnalyzer = None
        MetricsCalculator = None
        UIComponentGenerator = None

import warnings
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import asdict
from jinja2 import Template
from collections import defaultdict

warnings.filterwarnings('ignore')


class AdvancedReportGenerator:
    """
    Enhanced report generator with advanced behavior analysis and modern UI/UX.
    Provides backward compatibility while using modular components when available.
    """
    
    def __init__(self):
        """Initialize the advanced report generator."""
        # Try to use modular components if available
        if EnhancedReportGenerator:
            self.enhanced_generator = EnhancedReportGenerator()
            self.behavior_analyzer = BehaviorAnalyzer()
            self.metrics_calculator = MetricsCalculator()
            self.ui_generator = UIComponentGenerator()
            self.use_modular = True
        else:
            self.use_modular = False
        
    def generate_report(self, analysis_data: Dict, output_file: str = "advanced_gitlab_analysis.html") -> str:
        """Generate an advanced comprehensive HTML report.
        
        Args:
            analysis_data: Dictionary containing analysis results
            output_file: Output HTML file path
            
        Returns:
            Path to the generated HTML file
        """
        if self.use_modular:
            # Use the enhanced modular generator
            try:
                return self.enhanced_generator.generate_report(analysis_data, output_file)
            except Exception as e:
                print(f"Modular generator failed ({e}), falling back to legacy method")
                return self._legacy_generate_report(analysis_data, output_file)
        else:
            # Use legacy method
            return self._legacy_generate_report(analysis_data, output_file)
    
    def _legacy_generate_report(self, analysis_data: Dict, output_file: str) -> str:
        """Legacy report generation method for backward compatibility."""
        # Extract data
        reviewer_stats = analysis_data.get('reviewer_stats')
        team_stats = analysis_data.get('team_stats', {})
        reviewer_comments = analysis_data.get('reviewer_comments', [])
        all_comments = analysis_data.get('all_comments', [])
        
        # Enhanced behavior analysis with detailed data
        developer_analysis = self._analyze_developer_treatment_detailed(all_comments)
        reviewer_analysis = self._analyze_reviewer_patterns_detailed(all_comments)
        advanced_insights = self._generate_advanced_insights(analysis_data)
        bias_analysis = self._analyze_bias_patterns(analysis_data)
        communication_patterns = self._analyze_communication_patterns(all_comments)
        team_dynamics = self._analyze_team_dynamics(team_stats, all_comments)
        summary = self._prepare_enhanced_summary(analysis_data, advanced_insights)
        
        # Get the enhanced HTML template
        template = self._create_enhanced_html_template()
        
        # Render the enhanced template
        html_content = template.render(
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            summary=summary,
            reviewer_stats=asdict(reviewer_stats) if reviewer_stats else {},
            advanced_insights=advanced_insights,
            bias_analysis=bias_analysis,
            communication_patterns=communication_patterns,
            team_dynamics=team_dynamics,
            developer_analysis=developer_analysis,
            reviewer_analysis=reviewer_analysis,
            analysis_period=analysis_data.get('analysis_period', 'N/A'),
            total_mrs=analysis_data.get('total_mrs_analyzed', 0)
        )
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return output_file
    
    def _analyze_developer_treatment_detailed(self, all_comments: List) -> Dict:
        """Analyze how each developer is treated by different reviewers with detailed data."""
        developer_analysis = {}
        
        # Group comments by MR author (developer)
        comments_by_developer = defaultdict(list)
        for comment in all_comments:
            comments_by_developer[comment.mr_author].append(comment)
        
        for developer, dev_comments in comments_by_developer.items():
            # Group by reviewer
            reviewer_sentiments = defaultdict(list)
            reviewer_actions = defaultdict(lambda: {'approved': 0, 'requested_changes': 0, 'commented': 0})
            reviewer_comments = defaultdict(list)
            
            for comment in dev_comments:
                reviewer_sentiments[comment.author].append(comment.sentiment_textblob)
                reviewer_actions[comment.author][comment.approval_status] += 1
                reviewer_comments[comment.author].append(comment)
            
            # Calculate statistics
            reviewer_stats = {}
            for reviewer, sentiments in reviewer_sentiments.items():
                avg_sentiment = sum(sentiments) / len(sentiments)
                actions = reviewer_actions[reviewer]
                total_reviews = sum(actions.values())
                
                # Enhanced treatment level determination
                toxicity_score = self._calculate_toxicity_score(reviewer, dev_comments)
                
                # Get negative comments with details
                negative_comments = [c for c in reviewer_comments[reviewer] if c.sentiment_textblob < -0.2]
                
                if avg_sentiment >= 0.2 and toxicity_score < 0.3:
                    treatment = "Very Supportive"
                    treatment_color = "#27ae60"
                    treatment_icon = "🤗"
                elif avg_sentiment >= 0.0 and toxicity_score < 0.5:
                    treatment = "Supportive"
                    treatment_color = "#2ecc71"
                    treatment_icon = "😊"
                elif avg_sentiment >= -0.2 and toxicity_score < 0.6:
                    treatment = "Neutral"
                    treatment_color = "#95a5a6"
                    treatment_icon = "😐"
                elif avg_sentiment >= -0.4 and toxicity_score < 0.8:
                    treatment = "Critical"
                    treatment_color = "#f39c12"
                    treatment_icon = "🤨"
                elif avg_sentiment >= -0.6:
                    treatment = "Very Critical"
                    treatment_color = "#e67e22"
                    treatment_icon = "😠"
                else:
                    treatment = "Potentially Toxic"
                    treatment_color = "#e74c3c"
                    treatment_icon = "🚨"
                
                # Identify negative patterns
                negative_patterns = self._identify_negative_patterns(reviewer, dev_comments)
                
                reviewer_stats[reviewer] = {
                    'avg_sentiment': avg_sentiment,
                    'review_count': len(sentiments),
                    'treatment': treatment,
                    'treatment_color': treatment_color,
                    'treatment_icon': treatment_icon,
                    'approval_rate': actions['approved'] / total_reviews if total_reviews > 0 else 0,
                    'change_request_rate': actions['requested_changes'] / total_reviews if total_reviews > 0 else 0,
                    'negative_patterns': negative_patterns,
                    'communication_style': self._determine_communication_style(sentiments, toxicity_score),
                    'negative_comments_count': len(negative_comments),
                    'negative_comments': negative_comments[:10],  # Limit to first 10 for display
                    'toxicity_score': toxicity_score,
                    'all_comments': reviewer_comments[reviewer]
                }
            
            # Overall statistics for this developer
            all_sentiments = [comment.sentiment_textblob for comment in dev_comments]
            overall_sentiment = sum(all_sentiments) / len(all_sentiments)
            
            # Find most and least supportive reviewers
            if reviewer_stats:
                most_supportive = max(reviewer_stats.items(), key=lambda x: x[1]['avg_sentiment'])
                least_supportive = min(reviewer_stats.items(), key=lambda x: x[1]['avg_sentiment'])
                sentiment_range = most_supportive[1]['avg_sentiment'] - least_supportive[1]['avg_sentiment']
                
                # Enhanced bias detection
                bias_indicators = []
                if overall_sentiment < -0.2:
                    bias_indicators.append("Receives generally negative feedback across the team")
                if sentiment_range > 0.6:
                    bias_indicators.append("Very inconsistent treatment from different reviewers")
                
                critical_reviewers = [r for r in reviewer_stats.values() 
                                    if r['treatment'] in ['Critical', 'Very Critical', 'Potentially Toxic']]
                if len(critical_reviewers) > len(reviewer_stats) * 0.5:
                    bias_indicators.append("Majority of reviewers are critical")
                
                # Check for toxic behavior patterns
                toxic_reviewers = [r for r in reviewer_stats.values() 
                                 if r['treatment'] == 'Potentially Toxic']
                if toxic_reviewers:
                    bias_indicators.append("Some reviewers show toxic behavior patterns")
                
                bias_risk = 'high' if len(bias_indicators) >= 3 else 'medium' if len(bias_indicators) >= 2 else 'low'
                
                # Generate recommendations
                recommendations = self._generate_developer_recommendations(bias_indicators, reviewer_stats)
                
                # Count total negative reviews received
                total_negative_reviews = sum(len([c for c in stats['all_comments'] if c.sentiment_textblob < -0.2]) 
                                           for stats in reviewer_stats.values())
                
                developer_analysis[developer] = {
                    'reviewer_stats': reviewer_stats,
                    'overall_sentiment': overall_sentiment,
                    'total_reviews': len(dev_comments),
                    'total_negative_reviews': total_negative_reviews,
                    'most_supportive_reviewer': most_supportive[0],
                    'least_supportive_reviewer': least_supportive[0],
                    'sentiment_range': sentiment_range,
                    'bias_indicators': bias_indicators,
                    'bias_risk': bias_risk,
                    'recommendations': recommendations,
                    'all_comments': dev_comments
                }
        
        return developer_analysis
    
    def _analyze_reviewer_patterns_detailed(self, all_comments: List) -> Dict:
        """Analyze detailed patterns for each reviewer."""
        reviewer_analysis = {}
        
        # Group comments by reviewer (author)
        comments_by_reviewer = defaultdict(list)
        for comment in all_comments:
            comments_by_reviewer[comment.author].append(comment)
        
        for reviewer, reviewer_comments in comments_by_reviewer.items():
            # Group by target developer
            target_sentiments = defaultdict(list)
            target_comments = defaultdict(list)
            
            for comment in reviewer_comments:
                target_sentiments[comment.mr_author].append(comment.sentiment_textblob)
                target_comments[comment.mr_author].append(comment)
            
            # Calculate detailed statistics
            negative_reviews_by_target = {}
            total_negative_reviews = 0
            
            for target, comments in target_comments.items():
                negative_comments = [c for c in comments if c.sentiment_textblob < -0.2]
                negative_reviews_by_target[target] = {
                    'count': len(negative_comments),
                    'comments': negative_comments,
                    'avg_sentiment': sum([c.sentiment_textblob for c in comments]) / len(comments),
                    'total_reviews': len(comments)
                }
                total_negative_reviews += len(negative_comments)
            
            # Overall reviewer statistics
            all_sentiments = [c.sentiment_textblob for c in reviewer_comments]
            avg_sentiment = sum(all_sentiments) / len(all_sentiments)
            toxicity_score = self._calculate_toxicity_score_for_reviewer(reviewer_comments)
            
            # Identify patterns
            patterns = self._identify_reviewer_patterns(reviewer_comments)
            
            # Determine reviewer risk level
            risk_level = 'low'
            if total_negative_reviews > len(reviewer_comments) * 0.4:
                risk_level = 'high'
            elif total_negative_reviews > len(reviewer_comments) * 0.2:
                risk_level = 'medium'
            
            reviewer_analysis[reviewer] = {
                'total_reviews': len(reviewer_comments),
                'total_negative_reviews': total_negative_reviews,
                'avg_sentiment': avg_sentiment,
                'toxicity_score': toxicity_score,
                'risk_level': risk_level,
                'patterns': patterns,
                'negative_reviews_by_target': negative_reviews_by_target,
                'targets_count': len(target_comments),
                'most_targeted': max(negative_reviews_by_target.items(), 
                                   key=lambda x: x[1]['count']) if negative_reviews_by_target else None
            }
        
        return reviewer_analysis
    
    def _calculate_toxicity_score_for_reviewer(self, comments: List) -> float:
        """Calculate toxicity score for a reviewer's comments."""
        if not comments:
            return 0.0
        
        negative_keywords = ['terrible', 'awful', 'horrible', 'stupid', 'dumb', 'ridiculous', 
                           'waste', 'nonsense', 'garbage', 'trash', 'pathetic', 'useless']
        
        toxicity_score = 0.0
        for comment in comments:
            body_lower = comment.body.lower()
            negative_count = sum(1 for keyword in negative_keywords if keyword in body_lower)
            toxicity_score += negative_count * 0.2
            
            # Check for personal attacks
            if any(phrase in body_lower for phrase in ['you are', 'you\'re', 'your fault']):
                toxicity_score += 0.3
        
        return min(1.0, toxicity_score / len(comments))
    
    def _identify_reviewer_patterns(self, comments: List) -> List[str]:
        """Identify patterns in a reviewer's behavior."""
        patterns = []
        
        if not comments:
            return patterns
        
        # Check for excessive commenting
        mr_comment_counts = defaultdict(int)
        for comment in comments:
            mr_comment_counts[comment.mr_title] += 1
        
        excessive_mrs = [count for count in mr_comment_counts.values() if count > 10]
        if len(excessive_mrs) > len(mr_comment_counts) * 0.3:
            patterns.append("Tends to over-comment on merge requests")
        
        # Check for consistently negative sentiment
        sentiments = [c.sentiment_textblob for c in comments]
        avg_sentiment = sum(sentiments) / len(sentiments)
        if avg_sentiment < -0.3:
            patterns.append("Consistently negative sentiment in reviews")
        
        # Check for nitpicking (short critical comments)
        short_critical = [c for c in comments if len(c.body) < 50 and c.sentiment_textblob < -0.2]
        if len(short_critical) > len(comments) * 0.4:
            patterns.append("Shows nitpicking behavior with short critical comments")
        
        # Check for blocking without constructive feedback
        change_requests = [c for c in comments if c.approval_status == 'requested_changes']
        if change_requests:
            constructive_keywords = ['suggest', 'recommend', 'consider', 'try', 'example']
            non_constructive = [c for c in change_requests 
                              if not any(keyword in c.body.lower() for keyword in constructive_keywords)]
            if len(non_constructive) > len(change_requests) * 0.6:
                patterns.append("Blocks MRs without providing constructive feedback")
        
        return patterns
    
    def _calculate_toxicity_score(self, reviewer: str, comments: List) -> float:
        """Calculate toxicity score for a reviewer's comments."""
        reviewer_comments = [c for c in comments if c.author == reviewer]
        if not reviewer_comments:
            return 0.0
        
        negative_keywords = ['terrible', 'awful', 'horrible', 'stupid', 'dumb', 'ridiculous', 
                           'waste', 'nonsense', 'garbage', 'trash', 'pathetic', 'useless']
        
        toxicity_score = 0.0
        for comment in reviewer_comments:
            body_lower = comment.body.lower()
            negative_count = sum(1 for keyword in negative_keywords if keyword in body_lower)
            toxicity_score += negative_count * 0.2
            
            # Check for personal attacks
            if any(phrase in body_lower for phrase in ['you are', 'you\'re', 'your fault']):
                toxicity_score += 0.3
        
        return min(1.0, toxicity_score / len(reviewer_comments))
    
    def _identify_negative_patterns(self, reviewer: str, comments: List) -> List[str]:
        """Identify negative patterns in reviewer behavior."""
        patterns = []
        reviewer_comments = [c for c in comments if c.author == reviewer]
        
        if not reviewer_comments:
            return patterns
        
        # Check for excessive commenting
        comment_counts_per_mr = defaultdict(int)
        for comment in reviewer_comments:
            comment_counts_per_mr[comment.mr_title] += 1
        
        excessive_mrs = [count for count in comment_counts_per_mr.values() if count > 10]
        if len(excessive_mrs) > len(comment_counts_per_mr) * 0.3:
            patterns.append("Tends to over-comment on merge requests")
        
        # Check for consistently negative sentiment
        sentiments = [c.sentiment_textblob for c in reviewer_comments]
        avg_sentiment = sum(sentiments) / len(sentiments)
        if avg_sentiment < -0.3:
            patterns.append("Consistently negative sentiment in reviews")
        
        # Check for nitpicking (short critical comments)
        short_critical = [c for c in reviewer_comments 
                         if len(c.body) < 50 and c.sentiment_textblob < -0.2]
        if len(short_critical) > len(reviewer_comments) * 0.4:
            patterns.append("Shows nitpicking behavior with short critical comments")
        
        # Check for blocking without constructive feedback
        change_requests = [c for c in reviewer_comments if c.approval_status == 'requested_changes']
        if change_requests:
            constructive_keywords = ['suggest', 'recommend', 'consider', 'try', 'example']
            non_constructive = [c for c in change_requests 
                              if not any(keyword in c.body.lower() for keyword in constructive_keywords)]
            if len(non_constructive) > len(change_requests) * 0.6:
                patterns.append("Blocks MRs without providing constructive feedback")
        
        return patterns
    
    def _determine_communication_style(self, sentiments: List[float], toxicity_score: float) -> str:
        """Determine communication style based on sentiment and toxicity."""
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        if avg_sentiment > 0.2 and toxicity_score < 0.2:
            return "Encouraging & Constructive"
        elif avg_sentiment > 0.0 and toxicity_score < 0.3:
            return "Professional & Balanced"
        elif avg_sentiment > -0.2 and toxicity_score < 0.4:
            return "Direct & Factual"
        elif avg_sentiment > -0.4 and toxicity_score < 0.6:
            return "Critical & Demanding"
        else:
            return "Harsh & Potentially Problematic"
    
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
        sentiments = [stats['avg_sentiment'] for stats in reviewer_stats.values()]
        if len(sentiments) > 1:
            sentiment_range = max(sentiments) - min(sentiments)
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
    
    def _generate_advanced_insights(self, analysis_data: Dict) -> Dict:
        """Generate advanced insights and pattern detection."""
        insights = {
            'bias_score': 0,
            'communication_style': 'neutral',
            'consistency_score': 0,
            'collaboration_index': 0,
            'patterns': [],
            'recommendations': [],
            'risk_factors': [],
            'strengths': []
        }
        
        reviewer_stats = analysis_data.get('reviewer_stats')
        if not reviewer_stats:
            return insights
        
        # Calculate bias score
        if hasattr(reviewer_stats, 'sentiment_by_author') and reviewer_stats.sentiment_by_author:
            sentiments = [sum(s)/len(s) for s in reviewer_stats.sentiment_by_author.values()]
            sentiment_std = np.std(sentiments) if len(sentiments) > 1 else 0
            sentiment_range = max(sentiments) - min(sentiments) if sentiments else 0
            
            # Bias score (0-100, higher = more biased)
            insights['bias_score'] = min(100, int((sentiment_std * 100 + sentiment_range * 50)))
            
            # Pattern detection
            if sentiment_range > 0.6:
                insights['patterns'].append("High sentiment variation between team members")
                insights['risk_factors'].append("Potential favoritism detected")
            
            if min(sentiments) < -0.3:
                insights['patterns'].append("Consistently negative towards some team members")
                insights['risk_factors'].append("Possible interpersonal conflicts")
        
        # Communication style analysis
        avg_sentiment = getattr(reviewer_stats, 'avg_sentiment_textblob', 0)
        if avg_sentiment > 0.3:
            insights['communication_style'] = 'supportive'
            insights['strengths'].append("Generally positive and encouraging")
        elif avg_sentiment < -0.2:
            insights['communication_style'] = 'critical'
            insights['risk_factors'].append("Tends to be overly critical")
        else:
            insights['communication_style'] = 'balanced'
            insights['strengths'].append("Maintains balanced communication tone")
        
        # Generate recommendations
        if insights['bias_score'] > 60:
            insights['recommendations'].append("Consider bias training and awareness sessions")
            insights['recommendations'].append("Implement structured review templates")
        
        if avg_sentiment < -0.1:
            insights['recommendations'].append("Focus on constructive feedback techniques")
        
        return insights
    
    def _analyze_bias_patterns(self, analysis_data: Dict) -> Dict:
        """Analyze potential bias patterns in detail."""
        bias_analysis = {
            'overall_risk': 'low',
            'specific_risks': [],
            'author_analysis': {},
            'mitigation_strategies': []
        }
        
        reviewer_stats = analysis_data.get('reviewer_stats')
        if not reviewer_stats or not hasattr(reviewer_stats, 'sentiment_by_author') or not reviewer_stats.sentiment_by_author:
            return bias_analysis
        
        # Analyze each author relationship
        for author, sentiments in reviewer_stats.sentiment_by_author.items():
            avg_sentiment = sum(sentiments) / len(sentiments)
            review_count = len(sentiments)
            sentiment_std = np.std(sentiments) if len(sentiments) > 1 else 0
            
            risk_level = 'low'
            patterns = []
            
            if avg_sentiment < -0.3:
                risk_level = 'high'
                patterns.append("Consistently negative sentiment")
                bias_analysis['specific_risks'].append(f"Potential bias against {author}")
            elif avg_sentiment < -0.1 and review_count > 3:
                risk_level = 'medium'
                patterns.append("Tendency towards negative feedback")
            
            bias_analysis['author_analysis'][author] = {
                'avg_sentiment': avg_sentiment,
                'review_count': review_count,
                'sentiment_std': sentiment_std,
                'risk_level': risk_level,
                'patterns': patterns
            }
        
        # Overall risk assessment
        high_risk_count = sum(1 for a in bias_analysis['author_analysis'].values() if a['risk_level'] == 'high')
        if high_risk_count > 0:
            bias_analysis['overall_risk'] = 'high'
        elif sum(1 for a in bias_analysis['author_analysis'].values() if a['risk_level'] == 'medium') > 1:
            bias_analysis['overall_risk'] = 'medium'
        
        # Mitigation strategies
        if bias_analysis['overall_risk'] in ['high', 'medium']:
            bias_analysis['mitigation_strategies'].extend([
                "Implement anonymous code review processes",
                "Use structured review checklists",
                "Regular bias awareness training",
                "Monitor review patterns regularly"
            ])
        
        return bias_analysis
    
    def _analyze_communication_patterns(self, all_comments: List) -> Dict:
        """Analyze communication patterns across the team."""
        patterns = {
            'average_comment_length': 0,
            'sentiment_distribution': {},
            'professionalism_score': 0
        }
        
        if not all_comments:
            return patterns
        
        # Comment length analysis
        lengths = [len(comment.body) for comment in all_comments]
        patterns['average_comment_length'] = np.mean(lengths)
        
        # Sentiment distribution
        sentiments = [comment.sentiment_textblob for comment in all_comments]
        patterns['sentiment_distribution'] = {
            'very_negative': sum(1 for s in sentiments if s < -0.3) / len(sentiments),
            'negative': sum(1 for s in sentiments if -0.3 <= s < -0.1) / len(sentiments),
            'neutral': sum(1 for s in sentiments if -0.1 <= s <= 0.1) / len(sentiments),
            'positive': sum(1 for s in sentiments if 0.1 < s <= 0.3) / len(sentiments),
            'very_positive': sum(1 for s in sentiments if s > 0.3) / len(sentiments)
        }
        
        # Professionalism score
        constructive_keywords = ['suggest', 'recommend', 'consider', 'improve', 'better']
        negative_keywords = ['terrible', 'awful', 'stupid', 'horrible', 'garbage']
        
        constructive_count = sum(1 for comment in all_comments 
                               if any(keyword in comment.body.lower() for keyword in constructive_keywords))
        negative_count = sum(1 for comment in all_comments 
                           if any(keyword in comment.body.lower() for keyword in negative_keywords))
        
        total_comments = len(all_comments)
        patterns['professionalism_score'] = max(0, 100 - (negative_count / total_comments * 100) + 
                                              (constructive_count / total_comments * 50))
        
        return patterns
    
    def _analyze_team_dynamics(self, team_stats: Dict, all_comments: List) -> Dict:
        """Analyze team dynamics and collaboration patterns."""
        dynamics = {
            'team_cohesion': 0,
            'collaboration_score': 0
        }
        
        if not all_comments:
            return dynamics
        
        # Team cohesion based on sentiment consistency
        sentiments = [comment.sentiment_textblob for comment in all_comments]
        if sentiments:
            sentiment_std = np.std(sentiments)
            dynamics['team_cohesion'] = max(0, 100 - (sentiment_std * 100))
        
        # Collaboration score based on interaction diversity
        interactions = defaultdict(set)
        for comment in all_comments:
            interactions[comment.author].add(comment.mr_author)
        
        if interactions:
            avg_interactions = np.mean([len(people) for people in interactions.values()])
            dynamics['collaboration_score'] = min(100, (avg_interactions / 5) * 100)
        
        return dynamics
    
    def _prepare_enhanced_summary(self, analysis_data: Dict, advanced_insights: Dict) -> Dict:
        """Prepare enhanced summary with advanced metrics."""
        reviewer_stats = analysis_data.get('reviewer_stats')
        team_stats = analysis_data.get('team_stats', {})
        
        summary = {
            'total_reviews': 0,
            'avg_sentiment': 0.0,
            'bias_risk_level': 'Low',
            'communication_style': 'Neutral'
        }
        
        if reviewer_stats:
            summary['total_reviews'] = getattr(reviewer_stats, 'total_reviews', 0)
            summary['avg_sentiment'] = getattr(reviewer_stats, 'avg_sentiment_textblob', 0.0)
            summary['communication_style'] = advanced_insights.get('communication_style', 'neutral').title()
            
            # Determine bias risk level
            bias_score = advanced_insights.get('bias_score', 0)
            if bias_score > 70:
                summary['bias_risk_level'] = 'High'
            elif bias_score > 40:
                summary['bias_risk_level'] = 'Medium'
            else:
                summary['bias_risk_level'] = 'Low'
        
        return summary
    
    def _create_enhanced_html_template(self) -> Template:
        """Create an enhanced HTML template with detailed developer and reviewer tabs."""
        template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 GitLab Developer Behavior Analysis</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 12px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white; 
            padding: 2rem; 
            text-align: center; 
        }
        .header h1 { 
            margin: 0; 
            font-size: 2.5rem; 
            font-weight: 700; 
        }
        .header p { 
            margin: 0.5rem 0 0 0; 
            opacity: 0.9; 
            font-size: 1.1rem; 
        }
        
        .nav-tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            margin: 0;
            padding: 0;
        }
        .nav-tab {
            flex: 1;
            padding: 1rem 1.5rem;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 600;
            color: #495057;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        .nav-tab:hover {
            background: #e9ecef;
            color: #3498db;
        }
        .nav-tab.active {
            background: white;
            color: #3498db;
            border-bottom-color: #3498db;
        }
        
        .tab-content {
            display: none;
            padding: 2rem;
            min-height: 600px;
        }
        .tab-content.active {
            display: block;
        }
        
        .summary { 
            background: linear-gradient(135deg, #ecf0f1 0%, #bdc3c7 100%); 
            padding: 1.5rem; 
            border-radius: 8px; 
            margin-bottom: 2rem; 
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        .metric { 
            background: #3498db; 
            color: white; 
            padding: 1rem; 
            border-radius: 8px; 
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .developer-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .developer-card { 
            background: #fff; 
            border: 1px solid #ddd; 
            padding: 1.5rem; 
            border-radius: 8px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .developer-card h3 {
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.5rem;
        }
        
        .treatment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 0.5rem;
            margin: 1rem 0;
        }
        .treatment-card { 
            padding: 0.75rem; 
            border-radius: 6px; 
            color: white; 
            text-align: center;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .comment-item {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-radius: 4px;
            border-left: 4px solid #f39c12;
        }
        .comment-meta {
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 0.5rem;
        }
        .comment-body {
            font-style: italic;
        }
        
        .risk-high { background: #e74c3c; }
        .risk-medium { background: #f39c12; }
        .risk-low { background: #27ae60; }
        
        .patterns-list {
            list-style: none;
            padding: 0;
        }
        .patterns-list li {
            background: #f8f9fa;
            padding: 0.5rem;
            margin: 0.25rem 0;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }
        
        .recommendations {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            padding: 1rem;
            border-radius: 6px;
            margin: 1rem 0;
        }
        .recommendations ul {
            margin: 0;
            padding-left: 1.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 GitLab Developer Behavior Analysis</h1>
            <p>Advanced analysis of review patterns and developer treatment</p>
            <p>Generated: {{ generated_at }}</p>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('overview')">📊 Overview</button>
            <button class="nav-tab" onclick="showTab('developers')">👥 Developer Analysis</button>
            <button class="nav-tab" onclick="showTab('reviewers')">🔍 Reviewer Patterns</button>
            <button class="nav-tab" onclick="showTab('insights')">🧠 Advanced Insights</button>
        </div>
        
        <div id="overview" class="tab-content active">
            <div class="summary">
                <h2>📊 Summary</h2>
                <div class="metrics-grid">
                    <div class="metric">
                        <div class="metric-value">{{ summary.total_reviews }}</div>
                        <div class="metric-label">Total Reviews</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ "%.2f"|format(summary.avg_sentiment) }}</div>
                        <div class="metric-label">Avg Sentiment</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ summary.bias_risk_level }}</div>
                        <div class="metric-label">Bias Risk</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{{ summary.communication_style }}</div>
                        <div class="metric-label">Communication Style</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="developers" class="tab-content">
            <h2>👥 Developer Treatment Analysis</h2>
            <div class="developer-grid">
                {% for developer, analysis in developer_analysis.items() %}
                <div class="developer-card">
                    <h3>{{ developer }}</h3>
                    <p><strong>Overall Sentiment:</strong> {{ "%.2f"|format(analysis.overall_sentiment) }}</p>
                    <p><strong>Total Reviews:</strong> {{ analysis.total_reviews }}</p>
                    <p><strong>Negative Reviews:</strong> {{ analysis.total_negative_reviews }}</p>
                    <p><strong>Bias Risk:</strong> <span class="risk-{{ analysis.bias_risk }}">{{ analysis.bias_risk|title }}</span></p>
                    
                    <h4>Reviewer Treatment:</h4>
                    <div class="treatment-grid">
                        {% for reviewer, stats in analysis.reviewer_stats.items() %}
                        <div class="treatment-card" style="background-color: {{ stats.treatment_color }}">
                            {{ stats.treatment_icon }} {{ reviewer }}<br>
                            {{ stats.treatment }}<br>
                            ({{ "%.2f"|format(stats.avg_sentiment) }})
                            {% if stats.negative_comments_count > 0 %}
                            <br><small>{{ stats.negative_comments_count }} negative comments</small>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    
                    {% if analysis.bias_indicators %}
                    <h4>⚠️ Bias Indicators:</h4>
                    <ul class="patterns-list">
                    {% for indicator in analysis.bias_indicators %}
                        <li>{{ indicator }}</li>
                    {% endfor %}
                    </ul>
                    {% endif %}
                    
                    <div class="recommendations">
                        <h4>💡 Recommendations:</h4>
                        <ul>
                        {% for rec in analysis.recommendations %}
                            <li>{{ rec }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                    
                    {% for reviewer, stats in analysis.reviewer_stats.items() %}
                        {% if stats.negative_comments %}
                        <h4>Negative Comments from {{ reviewer }}:</h4>
                        {% for comment in stats.negative_comments %}
                        <div class="comment-item">
                            <div class="comment-meta">
                                MR: {{ comment.mr_title }} | Sentiment: {{ "%.2f"|format(comment.sentiment_textblob) }}
                            </div>
                            <div class="comment-body">{{ comment.body[:200] }}{% if comment.body|length > 200 %}...{% endif %}</div>
                        </div>
                        {% endfor %}
                        {% endif %}
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div id="reviewers" class="tab-content">
            <h2>🔍 Reviewer Pattern Analysis</h2>
            <div class="developer-grid">
                {% for reviewer, analysis in reviewer_analysis.items() %}
                <div class="developer-card">
                    <h3>{{ reviewer }}</h3>
                    <p><strong>Total Reviews:</strong> {{ analysis.total_reviews }}</p>
                    <p><strong>Negative Reviews:</strong> {{ analysis.total_negative_reviews }}</p>
                    <p><strong>Avg Sentiment:</strong> {{ "%.2f"|format(analysis.avg_sentiment) }}</p>
                    <p><strong>Risk Level:</strong> <span class="risk-{{ analysis.risk_level }}">{{ analysis.risk_level|title }}</span></p>
                    <p><strong>Targets:</strong> {{ analysis.targets_count }} developers</p>
                    
                    {% if analysis.patterns %}
                    <h4>📈 Behavior Patterns:</h4>
                    <ul class="patterns-list">
                    {% for pattern in analysis.patterns %}
                        <li>{{ pattern }}</li>
                    {% endfor %}
                    </ul>
                    {% endif %}
                    
                    {% if analysis.most_targeted %}
                    <h4>Most Targeted Developer:</h4>
                    <p><strong>{{ analysis.most_targeted[0] }}</strong> - {{ analysis.most_targeted[1].count }} negative reviews</p>
                    {% endif %}
                    
                    <h4>Negative Reviews by Target:</h4>
                    {% for target, data in analysis.negative_reviews_by_target.items() %}
                        {% if data.count > 0 %}
                        <div style="margin: 0.5rem 0; padding: 0.5rem; background: #f8f9fa; border-radius: 4px;">
                            <strong>{{ target }}:</strong> {{ data.count }} negative reviews 
                            ({{ "%.2f"|format(data.avg_sentiment) }} avg sentiment)
                        </div>
                        {% endif %}
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div id="insights" class="tab-content">
            <h2>🧠 Advanced Insights</h2>
            <div class="summary">
                <p><strong>Communication Style:</strong> {{ advanced_insights.communication_style|title }}</p>
                <p><strong>Bias Score:</strong> {{ advanced_insights.bias_score }}/100</p>
                
                {% if advanced_insights.patterns %}
                <h3>📈 Patterns Detected:</h3>
                <ul class="patterns-list">
                {% for pattern in advanced_insights.patterns %}
                    <li>{{ pattern }}</li>
                {% endfor %}
                </ul>
                {% endif %}
                
                {% if advanced_insights.risk_factors %}
                <h3>⚠️ Risk Factors:</h3>
                <ul class="patterns-list">
                {% for risk in advanced_insights.risk_factors %}
                    <li>{{ risk }}</li>
                {% endfor %}
                </ul>
                {% endif %}
                
                {% if advanced_insights.strengths %}
                <h3>✅ Strengths:</h3>
                <ul class="patterns-list">
                {% for strength in advanced_insights.strengths %}
                    <li>{{ strength }}</li>
                {% endfor %}
                </ul>
                {% endif %}
                
                {% if advanced_insights.recommendations %}
                <div class="recommendations">
                    <h3>💡 Recommendations:</h3>
                    <ul>
                    {% for rec in advanced_insights.recommendations %}
                        <li>{{ rec }}</li>
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.nav-tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }
    </script>
</body>
</html>
        '''
        return Template(template_str)
