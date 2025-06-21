"""
Report generator for GitLab review analysis.

This module provides functionality to generate comprehensive HTML reports
with visualizations and detailed analysis of reviewer behavior and bias patterns.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from jinja2 import Template

from data_models import AnalysisResult, DeveloperTreatment, BiasAnalysis, BiasRiskLevel
from visualization import VisualizationGenerator


class ReportGenerator:
    """Generates HTML reports with analysis results and visualizations."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.visualization_generator = VisualizationGenerator()
    
    def generate_report(self, analysis_result: AnalysisResult, 
                       output_file: str = "gitlab_review_analysis.html") -> str:
        """Generate a comprehensive HTML report.
        
        Args:
            analysis_result: Analysis result data
            output_file: Output HTML file path
            
        Returns:
            Path to the generated HTML file
        """
        # Generate visualizations
        visualizations = self._generate_visualizations(analysis_result)
        
        # Prepare report data
        report_data = self._prepare_report_data(analysis_result, visualizations)
        
        # Get HTML template
        template = self._create_html_template()
        
        # Render the template
        html_content = template.render(**report_data)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _generate_visualizations(self, analysis_result: AnalysisResult) -> Dict[str, str]:
        """Generate visualizations for the report.
        
        Args:
            analysis_result: Analysis result data
            
        Returns:
            Dictionary mapping visualization names to base64-encoded images
        """
        visualizations = {}
        
        # Only generate visualizations if we have developer treatment data
        if analysis_result.developer_treatment:
            # Sentiment comparison across team members
            visualizations['sentiment_comparison'] = self.visualization_generator.generate_sentiment_comparison_chart(
                analysis_result.developer_treatment
            )
            
            # Team interaction heatmap
            visualizations['team_interaction'] = self.visualization_generator.generate_team_interaction_heatmap(
                analysis_result.developer_treatment
            )
            
            # Bias risk distribution
            visualizations['bias_risk'] = self.visualization_generator.generate_bias_risk_chart(
                analysis_result.developer_treatment
            )
            
            # Negative behavior patterns
            visualizations['negative_patterns'] = self.visualization_generator.generate_comparative_behavior_chart(
                analysis_result.developer_treatment
            )
        
        # Sentiment timeline (if we have comments)
        if analysis_result.all_comments:
            visualizations['sentiment_timeline'] = self.visualization_generator.generate_sentiment_timeline(
                analysis_result.all_comments
            )
        
        # If we have a specific reviewer, generate reviewer-specific visualizations
        if analysis_result.reviewer_stats and analysis_result.reviewer_comments:
            reviewer_name = analysis_result.reviewer_stats.reviewer_name
            
            # Reviewer sentiment timeline
            visualizations['reviewer_timeline'] = self.visualization_generator.generate_sentiment_timeline(
                analysis_result.reviewer_comments, reviewer_name
            )
            
            # If we have developer treatment data for this reviewer
            for developer, treatment in analysis_result.developer_treatment.items():
                if reviewer_name in treatment.reviewer_stats:
                    # Generate reviewer behavior chart for this developer
                    visualizations[f'reviewer_behavior_{developer}'] = self.visualization_generator.generate_reviewer_behavior_chart(
                        developer, treatment.reviewer_stats
                    )
                    break
        
        return visualizations
    
    def _prepare_report_data(self, analysis_result: AnalysisResult, 
                           visualizations: Dict[str, str]) -> Dict[str, Any]:
        """Prepare data for the report template.
        
        Args:
            analysis_result: Analysis result data
            visualizations: Dictionary of visualizations
            
        Returns:
            Dictionary with data for the report template
        """
        # Basic report data
        report_data = {
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'analysis_period': analysis_result.analysis_period,
            'total_mrs': analysis_result.total_mrs_analyzed,
            'visualizations': visualizations,
            'reviewer_stats': analysis_result.reviewer_stats,
            'team_stats': analysis_result.team_stats,
            'developer_treatments': analysis_result.developer_treatment,
            'bias_analysis': analysis_result.bias_analysis,
            'has_team_analysis': bool(analysis_result.developer_treatment),
            'has_reviewer_analysis': bool(analysis_result.reviewer_stats),
            'has_bias_analysis': bool(analysis_result.bias_analysis)
        }
        
        # Prepare summary data
        summary = self._prepare_summary(analysis_result)
        report_data['summary'] = summary
        
        # Prepare negative behavior documentation
        negative_behavior = self._document_negative_behavior(analysis_result)
        report_data['negative_behavior'] = negative_behavior
        
        return report_data
    
    def _prepare_summary(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Prepare summary data for the report.
        
        Args:
            analysis_result: Analysis result data
            
        Returns:
            Dictionary with summary data
        """
        summary = {
            'title': 'GitLab Review Sentiment Analysis',
            'subtitle': 'Analyzing reviewer behavior and potential bias',
            'total_reviews': 0,
            'avg_sentiment': 0.0,
            'bias_risk_level': 'Low',
            'bias_risk_color': '#27ae60',
            'key_findings': [],
            'recommendations': []
        }
        
        # Add reviewer-specific summary if available
        if analysis_result.reviewer_stats:
            reviewer_stats = analysis_result.reviewer_stats
            summary['total_reviews'] = reviewer_stats.total_reviews
            summary['avg_sentiment'] = reviewer_stats.avg_sentiment_textblob
            
            # Add key findings
            if reviewer_stats.avg_sentiment_textblob < -0.2:
                summary['key_findings'].append("Overall negative sentiment in reviews")
            
            if reviewer_stats.requested_changes_count / max(reviewer_stats.total_reviews, 1) > 0.6:
                summary['key_findings'].append("High rate of requested changes")
            
            # Check for sentiment variation
            if reviewer_stats.sentiment_by_author:
                sentiments = [sum(s)/len(s) for s in reviewer_stats.sentiment_by_author.values()]
                sentiment_range = max(sentiments) - min(sentiments) if sentiments else 0
                
                if sentiment_range > 0.4:
                    summary['key_findings'].append(f"High sentiment variation between authors ({sentiment_range:.2f})")
                    
                    # Find most negative sentiment
                    most_negative_author = min(
                        reviewer_stats.sentiment_by_author.items(),
                        key=lambda x: sum(x[1]) / len(x[1])
                    )
                    avg_negative = sum(most_negative_author[1]) / len(most_negative_author[1])
                    
                    if avg_negative < -0.2:
                        summary['key_findings'].append(
                            f"Potentially negative sentiment towards {most_negative_author[0]} ({avg_negative:.2f})"
                        )
        
        # Add team-wide summary if available
        if analysis_result.bias_analysis:
            bias_analysis = analysis_result.bias_analysis
            
            # Set bias risk level
            if bias_analysis.overall_risk == BiasRiskLevel.HIGH:
                summary['bias_risk_level'] = 'High'
                summary['bias_risk_color'] = '#e74c3c'
            elif bias_analysis.overall_risk == BiasRiskLevel.MEDIUM:
                summary['bias_risk_level'] = 'Medium'
                summary['bias_risk_color'] = '#f39c12'
            
            # Add specific risks to key findings
            for risk in bias_analysis.specific_risks:
                summary['key_findings'].append(risk)
            
            # Add mitigation strategies to recommendations
            summary['recommendations'].extend(bias_analysis.mitigation_strategies)
        
        # Add developer treatment recommendations if available
        if analysis_result.developer_treatment:
            # Collect all unique recommendations
            all_recommendations = set()
            for treatment in analysis_result.developer_treatment.values():
                all_recommendations.update(treatment.recommendations)
            
            # Add to summary recommendations (excluding generic ones)
            for rec in all_recommendations:
                if "appears fair and balanced" not in rec:
                    summary['recommendations'].append(rec)
        
        # If no key findings, add a positive note
        if not summary['key_findings']:
            summary['key_findings'].append("No significant bias patterns detected")
        
        # If no recommendations, add a generic one
        if not summary['recommendations']:
            summary['recommendations'].append("Continue monitoring review patterns regularly")
        
        return summary
    
    def _document_negative_behavior(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Document instances of negative behavior.
        
        Args:
            analysis_result: Analysis result data
            
        Returns:
            Dictionary with negative behavior documentation
        """
        documentation = {
            'instances': [],
            'reviewers': set(),
            'targets': set(),
            'categories': set(),
            'count': 0
        }
        
        # Collect negative behavior instances from developer treatments
        if analysis_result.developer_treatment:
            for developer, treatment in analysis_result.developer_treatment.items():
                for reviewer, stats in treatment.reviewer_stats.items():
                    if 'negative_comments' in stats:
                        for instance in stats['negative_comments']:
                            # Add to documentation
                            documentation['instances'].append({
                                'reviewer': reviewer,
                                'target': developer,
                                'comment': instance['comment'].body,
                                'mr_title': instance['comment'].mr_title,
                                'created_at': instance['comment'].created_at.strftime("%Y-%m-%d"),
                                'sentiment': instance['comment'].sentiment.textblob_score,
                                'categories': instance['categories'],
                                'severity': instance['severity'],
                                'toxicity_score': instance['toxicity_score'],
                                'constructiveness_score': instance['constructiveness_score']
                            })
                            
                            # Update metadata
                            documentation['reviewers'].add(reviewer)
                            documentation['targets'].add(developer)
                            documentation['categories'].update(instance['categories'])
        
        # Convert sets to lists for JSON serialization
        documentation['reviewers'] = list(documentation['reviewers'])
        documentation['targets'] = list(documentation['targets'])
        documentation['categories'] = list(documentation['categories'])
        documentation['count'] = len(documentation['instances'])
        
        # Sort instances by toxicity score (most toxic first)
        documentation['instances'] = sorted(
            documentation['instances'], 
            key=lambda x: x['toxicity_score'], 
            reverse=True
        )
        
        return documentation
    
    def _create_html_template(self) -> Template:
        """Create the HTML template for the report.
        
        Returns:
            Jinja2 Template object
        """
        # Load template from file if it exists, otherwise use a simple template
        template_path = Path("templates/report_template.html")
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                return Template(f.read())
        
        # Advanced template with better styling
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitLab Review Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --info-color: #17a2b8;
            --light-bg: #f8f9fa;
            --dark-bg: #343a40;
            --border-radius: 12px;
            --box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--primary-color);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .main-container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            overflow: hidden;
        }
        
        /* Header Styles */
        .header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            position: relative;
            z-index: 1;
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }
        
        /* Navigation */
        .nav-container {
            background: white;
            padding: 0 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .nav-tabs {
            display: flex;
            justify-content: center;
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .nav-tab {
            flex: 1;
            padding: 1.2rem 1.5rem;
            text-align: center;
            background: none;
            border: none;
            cursor: pointer;
            transition: var(--transition);
            font-weight: 600;
            font-size: 0.95rem;
            color: var(--primary-color);
            border-bottom: 3px solid transparent;
            white-space: nowrap;
        }
        
        .nav-tab:hover {
            background: rgba(52, 152, 219, 0.1);
            color: var(--secondary-color);
        }
        
        .nav-tab.active {
            color: var(--secondary-color);
            border-bottom-color: var(--secondary-color);
            background: rgba(52, 152, 219, 0.05);
        }
        
        /* Content */
        .content {
            padding: 2.5rem;
            min-height: 600px;
        }
        
        .tab-content {
            display: none;
            animation: fadeInUp 0.6s ease-out;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Cards and Metrics */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .metric-card {
            background: white;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            box-shadow: var(--box-shadow);
            border-left: 4px solid var(--secondary-color);
            transition: var(--transition);
            position: relative;
            overflow: hidden;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        
        /* Charts */
        .chart-container {
            background: white;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: var(--box-shadow);
        }
        
        .chart-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .chart-image {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 0 auto;
        }
        
        /* Findings and Recommendations */
        .findings-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: var(--border-radius);
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: var(--box-shadow);
        }
        
        .findings-list {
            list-style: none;
            padding: 0;
            margin: 1rem 0;
        }
        
        .findings-list li {
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border-left: 4px solid var(--warning-color);
        }
        
        .recommendations-list {
            list-style: none;
            padding: 0;
            margin: 1rem 0;
        }
        
        .recommendations-list li {
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border-left: 4px solid var(--info-color);
        }
        
        /* Negative Behavior Documentation */
        .negative-behavior-container {
            background: white;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: var(--box-shadow);
        }
        
        .behavior-instance {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            border-left: 4px solid var(--warning-color);
        }
        
        .behavior-instance.high {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-left: 4px solid var(--danger-color);
        }
        
        .behavior-instance.medium {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-left: 4px solid var(--warning-color);
        }
        
        .behavior-instance.low {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-left: 4px solid var(--info-color);
        }
        
        .behavior-meta {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .behavior-categories {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 0.5rem 0;
        }
        
        .behavior-category {
            background: rgba(0,0,0,0.1);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .behavior-comment {
            font-style: italic;
            margin: 0.5rem 0;
            padding: 0.5rem;
            background: rgba(255,255,255,0.5);
            border-radius: 4px;
        }
        
        .behavior-scores {
            display: flex;
            gap: 1rem;
            margin-top: 0.5rem;
            font-size: 0.8rem;
        }
        
        .behavior-score {
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            background: rgba(0,0,0,0.05);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .nav-tabs {
                flex-direction: column;
            }
            
            .nav-tab {
                border-bottom: 1px solid #eee;
                border-left: 3px solid transparent;
            }
            
            .nav-tab.active {
                border-left-color: var(--secondary-color);
                border-bottom-color: transparent;
            }
            
            .metrics-grid {
                grid-template-columns: 1fr;
            }
            
            .content {
                padding: 1.5rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Header -->
        <header class="header">
            <h1>{{ summary.title }}</h1>
            <div class="subtitle">
                {{ summary.subtitle }}<br>
                Generated on {{ generated_at }} | Analysis Period: {{ analysis_period }} | MRs Analyzed: {{ total_mrs }}
            </div>
        </header>
        
        <!-- Navigation -->
        <nav class="nav-container">
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('overview')">
                    Overview
                </button>
                {% if has_team_analysis %}
                <button class="nav-tab" onclick="showTab('team-analysis')">
                    Team Analysis
                </button>
                {% endif %}
                {% if has_reviewer_analysis %}
                <button class="nav-tab" onclick="showTab('reviewer-analysis')">
                    Reviewer Analysis
                </button>
                {% endif %}
                {% if negative_behavior.count > 0 %}
                <button class="nav-tab" onclick="showTab('negative-behavior')">
                    Negative Behavior
                </button>
                {% endif %}
                {% if has_bias_analysis %}
                <button class="nav-tab" onclick="showTab('bias-analysis')">
                    Bias Analysis
                </button>
                {% endif %}
            </div>
        </nav>
        
        <!-- Content -->
        <main class="content">
            <!-- Overview Tab -->
            <section id="overview" class="tab-content active">
                <h2>Executive Summary</h2>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{{ summary.total_reviews }}</div>
                        <div class="metric-label">Total Reviews</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.3f"|format(summary.avg_sentiment) }}</div>
                        <div class="metric-label">Average Sentiment</div>
                    </div>
                    
                    <div class="metric-card" style="border-left-color: {{ summary.bias_risk_color }};">
                        <div class="metric-value">{{ summary.bias_risk_level }}</div>
                        <div class="metric-label">Bias Risk Level</div>
                    </div>
                </div>
                
                <div class="findings-container">
                    <h3>Key Findings</h3>
                    <ul class="findings-list">
                        {% for finding in summary.key_findings %}
                        <li>{{ finding }}</li>
                        {% endfor %}
                    </ul>
                    
                    <h3>Recommendations</h3>
                    <ul class="recommendations-list">
                        {% for recommendation in summary.recommendations %}
                        <li>{{ recommendation }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                {% if 'sentiment_timeline' in visualizations %}
                <div class="chart-container">
                    <div class="chart-title">Sentiment Timeline</div>
                    <img class="chart-image" src="{{ visualizations.sentiment_timeline }}" alt="Sentiment Timeline">
                </div>
                {% endif %}
            </section>
            
            {% if has_team_analysis %}
            <!-- Team Analysis Tab -->
            <section id="team-analysis" class="tab-content">
                <h2>Team Analysis</h2>
                
                {% if 'sentiment_comparison' in visualizations %}
                <div class="chart-container">
                    <div class="chart-title">Sentiment Comparison Across Team Members</div>
                    <img class="chart-image" src="{{ visualizations.sentiment_comparison }}" alt="Sentiment Comparison">
                </div>
                {% endif %}
                
                {% if 'team_interaction' in visualizations %}
                <div class="chart-container">
                    <div class="chart-title">Team Interaction Patterns</div>
                    <img class="chart-image" src="{{ visualizations.team_interaction }}" alt="Team Interaction">
                </div>
                {% endif %}
                
                {% if 'bias_risk' in visualizations %}
                <div class="chart-container">
                    <div class="chart-title">Bias Risk Distribution</div>
                    <img class="chart-image" src="{{ visualizations.bias_risk }}" alt="Bias Risk Distribution">
                </div>
                {% endif %}
                
                {% if 'negative_patterns' in visualizations %}
                <div class="chart-container">
                    <div class="chart-title">Negative Behavior Patterns</div>
                    <img class="chart-image" src="{{ visualizations.negative_patterns }}" alt="Negative Behavior Patterns">
                </div>
                {% endif %}
                
                <div class="findings-container">
                    <h3>Developer Treatment Summary</h3>
                    
                    {% for developer, treatment in developer_treatments.items() %}
                    <div style="margin: 1rem 0; padding: 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                        <h4>{{ developer }}</h4>
                        <p><strong>Overall Sentiment:</strong> {{ "%.3f"|format(treatment.overall_sentiment) }}</p>
                        <p><strong>Total Reviews:</strong> {{ treatment.total_reviews }}</p>
                        <p><strong>Negative Reviews:</strong> {{ treatment.total_negative_reviews }}</p>
                        <p><strong>Bias Risk:</strong> {{ treatment.bias_risk.value }}</p>
                        
                        {% if treatment.bias_indicators %}
                        <div style="margin-top: 0.5rem;">
                            <strong>Bias Indicators:</strong>
                            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                                {% for indicator in treatment.bias_indicators %}
                                <li>{{ indicator }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </section>
            {% endif %}
            
            {% if has_reviewer_analysis %}
            <!-- Reviewer Analysis Tab -->
            <section id="reviewer-analysis" class="tab-content">
                <h2>Reviewer Analysis: {{ reviewer_stats.reviewer_name }}</h2>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{{ reviewer_stats.total_reviews }}</div>
                        <div class="metric-label">Total Reviews</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-value">{{ reviewer_stats.approved_count }}</div>
                        <div class="metric-label">Approvals</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-value">{{ reviewer_stats.requested_changes_count }}</div>
                        <div class="metric-label">Change Requests</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.3f"|format(reviewer_stats.avg_sentiment_textblob) }}</div>
                        <div class="metric-label">Average Sentiment</div>
                    </div>
                </div>
                
                {% if 'reviewer_timeline' in visualizations %}
                <div class="chart-container">
                    <div class="chart-title">Sentiment Timeline for {{ reviewer_stats.reviewer_name }}</div>
                    <img class="chart-image" src="{{ visualizations.reviewer_timeline }}" alt="Reviewer Sentiment Timeline">
                </div>
                {% endif %}
                
                <div class="findings-container">
                    <h3>Sentiment by Author</h3>
                    
                    {% if reviewer_stats.sentiment_by_author %}
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; margin: 1rem 0;">
                            <thead>
                                <tr style="background: #f8f9fa; text-align: left;">
                                    <th style="padding: 0.5rem;">Author</th>
                                    <th style="padding: 0.5rem;">Reviews</th>
                                    <th style="padding: 0.5rem;">Avg Sentiment</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for author, stats in reviewer_stats.sentiment_by_author.items() %}
                                <tr style="border-bottom: 1px solid #eee;">
                                    <td style="padding: 0.5rem;">{{ author }}</td>
                                    <td style="padding: 0.5rem;">{{ stats.count }}</td>
                                    <td style="padding: 0.5rem;">{{ "%.3f"|format(stats.avg_sentiment) }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% endif %}
                </div>
            </section>
            {% endif %}
            
            {% if negative_behavior.count > 0 %}
            <!-- Negative Behavior Tab -->
            <section id="negative-behavior" class="tab-content">
                <h2>Negative Behavior Documentation</h2>
                <p>Documented Instances: {{ negative_behavior.count }}</p>
                
                {% for instance in negative_behavior.instances %}
                <div class="behavior-instance {{ instance.severity }}">
                    <div class="behavior-meta">
                        <span><strong>Reviewer:</strong> {{ instance.reviewer }}</span>
                        <span><strong>Target:</strong> {{ instance.target }}</span>
                    </div>
                    <div class="behavior-comment">
                        <p>"{{ instance.comment }}"</p>
                    </div>
                    <div class="behavior-scores">
                        <span class="behavior-score">Sentiment: {{ "%.2f"|format(instance.sentiment) }}</span>
                        <span class="behavior-score">Toxicity: {{ "%.2f"|format(instance.toxicity_score) }}</span>
                    </div>
                </div>
                {% endfor %}
            </section>
            {% endif %}
            
            {% if has_bias_analysis %}
            <!-- Bias Analysis Tab -->
            <section id="bias-analysis" class="tab-content">
                <h2>Bias Analysis</h2>
                
                <div class="metrics-grid">
                    <div class="metric-card" style="border-left-color: {{ bias_analysis.risk_color }};">
                        <div class="metric-value">{{ bias_analysis.overall_risk.value }}</div>
                        <div class="metric-label">Overall Bias Risk</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-value">{{ bias_analysis.bias_patterns_count }}</div>
                        <div class="metric-label">Bias Patterns Detected</div>
                    </div>
                </div>
                
                <div class="findings-container">
                    <h3>Specific Bias Risks</h3>
                    <ul class="findings-list">
                        {% for risk in bias_analysis.specific_risks %}
                        <li>{{ risk }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                {% if 'bias_distribution' in visualizations %}
                <div class="chart-container">
                    <div class="chart-title">Bias Distribution</div>
                    <img class="chart-image" src="{{ visualizations.bias_distribution }}" alt="Bias Distribution">
                </div>
                {% endif %}
            </section>
            {% endif %}
        </main>
    </div>
    
    <script>
        function showTab(tabId) {
            // Hide all tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            
            // Update active tab button
            const buttons = document.querySelectorAll('.nav-tab');
            buttons.forEach(button => button.classList.remove('active'));
            event.currentTarget.classList.add('active');
        }
    </script>
</body>
</html>
"""
        
        return Template(template_str)
