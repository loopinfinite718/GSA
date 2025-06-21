"""
Visualization module for GitLab review analysis.

This module provides functions for generating charts and visualizations
to compare bias patterns across team members and illustrate review behavior.
"""

import os
import base64
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

from data_models import ReviewComment, DeveloperTreatment, BiasRiskLevel


class VisualizationGenerator:
    """Generates visualizations for GitLab review analysis."""
    
    def __init__(self):
        """Initialize the visualization generator with default settings."""
        # Set up styling
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'neutral': '#95a5a6'
        }
        
        self.treatment_colors = {
            'Very Supportive': '#27ae60',
            'Supportive': '#2ecc71',
            'Neutral': '#95a5a6',
            'Critical': '#f39c12',
            'Very Critical': '#e67e22',
            'Potentially Toxic': '#e74c3c'
        }
        
        self.risk_colors = {
            BiasRiskLevel.LOW: '#27ae60',
            BiasRiskLevel.MEDIUM: '#f39c12',
            BiasRiskLevel.HIGH: '#e74c3c'
        }
        
        # Set default style
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette('viridis')
    
    def generate_sentiment_comparison_chart(self, developer_treatments: Dict[str, DeveloperTreatment]) -> str:
        """Generate a chart comparing sentiment across developers.
        
        Args:
            developer_treatments: Dictionary mapping developer names to their treatment analysis
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=(10, 6))
        
        # Extract data
        developers = []
        sentiments = []
        colors = []
        
        for developer, treatment in developer_treatments.items():
            developers.append(developer)
            sentiments.append(treatment.overall_sentiment)
            
            # Color based on bias risk
            if treatment.bias_risk == BiasRiskLevel.HIGH:
                colors.append(self.risk_colors[BiasRiskLevel.HIGH])
            elif treatment.bias_risk == BiasRiskLevel.MEDIUM:
                colors.append(self.risk_colors[BiasRiskLevel.MEDIUM])
            else:
                colors.append(self.risk_colors[BiasRiskLevel.LOW])
        
        # Sort by sentiment
        sorted_data = sorted(zip(developers, sentiments, colors), key=lambda x: x[1])
        developers, sentiments, colors = zip(*sorted_data) if sorted_data else ([], [], [])
        
        # Create horizontal bar chart
        bars = plt.barh(developers, sentiments, color=colors)
        
        # Add a vertical line at 0
        plt.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
        
        # Add labels and title
        plt.xlabel('Average Sentiment Score (-1 to 1)')
        plt.title('Sentiment Comparison Across Team Members', fontsize=14, fontweight='bold')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width + 0.01 if width > 0 else width - 0.08
            plt.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                    va='center', fontsize=9)
        
        plt.tight_layout()
        
        # Convert to base64 for embedding in HTML
        return self._fig_to_base64(plt.gcf())
    
    def generate_reviewer_behavior_chart(self, developer_name: str, 
                                       reviewer_stats: Dict[str, Dict[str, Any]]) -> str:
        """Generate a chart showing how reviewers treat a specific developer.
        
        Args:
            developer_name: Name of the developer being analyzed
            reviewer_stats: Dictionary of reviewer statistics
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=(10, 6))
        
        # Extract data
        reviewers = []
        sentiments = []
        colors = []
        
        for reviewer, stats in reviewer_stats.items():
            reviewers.append(reviewer)
            sentiments.append(stats['avg_sentiment'])
            colors.append(self.treatment_colors.get(stats['treatment'], self.colors['neutral']))
        
        # Sort by sentiment
        sorted_data = sorted(zip(reviewers, sentiments, colors), key=lambda x: x[1])
        reviewers, sentiments, colors = zip(*sorted_data) if sorted_data else ([], [], [])
        
        # Create horizontal bar chart
        bars = plt.barh(reviewers, sentiments, color=colors)
        
        # Add a vertical line at 0
        plt.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
        
        # Add labels and title
        plt.xlabel('Average Sentiment Score (-1 to 1)')
        plt.title(f'How Reviewers Treat {developer_name}', fontsize=14, fontweight='bold')
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width + 0.01 if width > 0 else width - 0.08
            plt.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                    va='center', fontsize=9)
        
        plt.tight_layout()
        
        # Convert to base64 for embedding in HTML
        return self._fig_to_base64(plt.gcf())
    
    def generate_team_interaction_heatmap(self, developer_treatments: Dict[str, DeveloperTreatment]) -> str:
        """Generate a heatmap showing team interaction patterns.
        
        Args:
            developer_treatments: Dictionary mapping developer names to their treatment analysis
            
        Returns:
            Base64-encoded PNG image
        """
        # Extract all reviewers and developers
        all_developers = set(developer_treatments.keys())
        all_reviewers = set()
        
        for treatment in developer_treatments.values():
            all_reviewers.update(treatment.reviewer_stats.keys())
        
        # Create a matrix of sentiment scores
        developers = sorted(list(all_developers))
        reviewers = sorted(list(all_reviewers))
        
        sentiment_matrix = np.zeros((len(reviewers), len(developers)))
        
        for i, reviewer in enumerate(reviewers):
            for j, developer in enumerate(developers):
                if developer in developer_treatments and reviewer in developer_treatments[developer].reviewer_stats:
                    sentiment_matrix[i, j] = developer_treatments[developer].reviewer_stats[reviewer]['avg_sentiment']
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        ax = sns.heatmap(
            sentiment_matrix, 
            annot=True, 
            fmt=".2f", 
            cmap="RdYlGn", 
            center=0,
            xticklabels=developers,
            yticklabels=reviewers,
            cbar_kws={'label': 'Average Sentiment Score'}
        )
        
        # Add labels and title
        plt.title('Team Interaction Sentiment Heatmap', fontsize=14, fontweight='bold')
        plt.xlabel('Developers (MR Authors)')
        plt.ylabel('Reviewers')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Convert to base64 for embedding in HTML
        return self._fig_to_base64(plt.gcf())
    
    def generate_bias_risk_chart(self, developer_treatments: Dict[str, DeveloperTreatment]) -> str:
        """Generate a chart showing bias risk levels across the team.
        
        Args:
            developer_treatments: Dictionary mapping developer names to their treatment analysis
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=(10, 6))
        
        # Count risk levels
        risk_counts = {
            BiasRiskLevel.LOW: 0,
            BiasRiskLevel.MEDIUM: 0,
            BiasRiskLevel.HIGH: 0
        }
        
        for treatment in developer_treatments.values():
            risk_counts[treatment.bias_risk] += 1
        
        # Create pie chart
        labels = ['Low Risk', 'Medium Risk', 'High Risk']
        sizes = [risk_counts[BiasRiskLevel.LOW], risk_counts[BiasRiskLevel.MEDIUM], risk_counts[BiasRiskLevel.HIGH]]
        colors = [self.risk_colors[BiasRiskLevel.LOW], self.risk_colors[BiasRiskLevel.MEDIUM], self.risk_colors[BiasRiskLevel.HIGH]]
        
        # Only include non-zero values
        non_zero_labels = []
        non_zero_sizes = []
        non_zero_colors = []
        
        for i, size in enumerate(sizes):
            if size > 0:
                non_zero_labels.append(labels[i])
                non_zero_sizes.append(size)
                non_zero_colors.append(colors[i])
        
        if non_zero_sizes:
            plt.pie(
                non_zero_sizes, 
                labels=non_zero_labels, 
                colors=non_zero_colors,
                autopct='%1.1f%%', 
                startangle=90,
                wedgeprops={'edgecolor': 'white', 'linewidth': 1}
            )
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            plt.axis('equal')
            
            plt.title('Bias Risk Distribution Across Team', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # Convert to base64 for embedding in HTML
            return self._fig_to_base64(plt.gcf())
        else:
            # Handle empty data case
            plt.text(0.5, 0.5, 'No bias risk data available', 
                    horizontalalignment='center', verticalalignment='center')
            plt.axis('off')
            return self._fig_to_base64(plt.gcf())
    
    def generate_sentiment_timeline(self, comments: List[ReviewComment], 
                                  reviewer_name: Optional[str] = None) -> str:
        """Generate a timeline of sentiment over time.
        
        Args:
            comments: List of review comments
            reviewer_name: Optional reviewer name to filter by
            
        Returns:
            Base64-encoded PNG image
        """
        plt.figure(figsize=(12, 6))
        
        # Filter comments if reviewer specified
        if reviewer_name:
            filtered_comments = [c for c in comments if c.author == reviewer_name]
        else:
            filtered_comments = comments
        
        # Sort by date
        sorted_comments = sorted(filtered_comments, key=lambda x: x.created_at)
        
        if not sorted_comments:
            plt.text(0.5, 0.5, 'No comment data available', 
                    horizontalalignment='center', verticalalignment='center')
            plt.axis('off')
            return self._fig_to_base64(plt.gcf())
        
        # Extract dates and sentiments
        dates = [c.created_at for c in sorted_comments]
        sentiments = [c.sentiment.textblob_score for c in sorted_comments]
        
        # Create scatter plot with trend line
        plt.scatter(dates, sentiments, alpha=0.6, c=sentiments, cmap='RdYlGn', vmin=-1, vmax=1)
        
        # Add trend line
        z = np.polyfit(range(len(dates)), sentiments, 1)
        p = np.poly1d(z)
        plt.plot(dates, p(range(len(dates))), "r--", alpha=0.8)
        
        # Add horizontal line at 0
        plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
        
        # Add labels and title
        plt.xlabel('Date')
        plt.ylabel('Sentiment Score')
        title = f'Sentiment Timeline for {reviewer_name}' if reviewer_name else 'Sentiment Timeline for All Reviewers'
        plt.title(title, fontsize=14, fontweight='bold')
        
        # Format x-axis dates
        plt.gcf().autofmt_xdate()
        
        # Add color bar
        cbar = plt.colorbar()
        cbar.set_label('Sentiment Score')
        
        plt.tight_layout()
        
        # Convert to base64 for embedding in HTML
        return self._fig_to_base64(plt.gcf())
    
    def generate_comparative_behavior_chart(self, developer_treatments: Dict[str, DeveloperTreatment]) -> str:
        """Generate a chart comparing negative behavior patterns across reviewers.
        
        Args:
            developer_treatments: Dictionary mapping developer names to their treatment analysis
            
        Returns:
            Base64-encoded PNG image
        """
        # Collect data on negative patterns
        reviewer_patterns = defaultdict(lambda: defaultdict(int))
        
        for treatment in developer_treatments.values():
            for reviewer, stats in treatment.reviewer_stats.items():
                for pattern in stats.get('negative_patterns', []):
                    reviewer_patterns[reviewer][pattern] += 1
        
        # Get top reviewers with negative patterns
        reviewer_counts = {r: sum(patterns.values()) for r, patterns in reviewer_patterns.items()}
        top_reviewers = sorted(reviewer_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if not top_reviewers:
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, 'No negative behavior patterns detected', 
                    horizontalalignment='center', verticalalignment='center')
            plt.axis('off')
            return self._fig_to_base64(plt.gcf())
        
        # Get all unique patterns
        all_patterns = set()
        for patterns in reviewer_patterns.values():
            all_patterns.update(patterns.keys())
        
        # Create data for chart
        reviewers = [r for r, _ in top_reviewers]
        pattern_data = {}
        
        for pattern in all_patterns:
            pattern_data[pattern] = [reviewer_patterns[reviewer].get(pattern, 0) for reviewer in reviewers]
        
        # Create grouped bar chart
        plt.figure(figsize=(12, 8))
        
        bar_width = 0.8 / len(pattern_data)
        index = np.arange(len(reviewers))
        
        for i, (pattern, counts) in enumerate(pattern_data.items()):
            plt.bar(index + i * bar_width, counts, bar_width, label=pattern)
        
        plt.xlabel('Reviewers')
        plt.ylabel('Frequency')
        plt.title('Negative Behavior Patterns by Reviewer', fontsize=14, fontweight='bold')
        plt.xticks(index + bar_width * (len(pattern_data) - 1) / 2, reviewers, rotation=45, ha='right')
        plt.legend(loc='best', fontsize='small')
        
        plt.tight_layout()
        
        # Convert to base64 for embedding in HTML
        return self._fig_to_base64(plt.gcf())
    
    def _fig_to_base64(self, fig) -> str:
        """Convert a matplotlib figure to base64 encoded string.
        
        Args:
            fig: Matplotlib figure
            
        Returns:
            Base64-encoded PNG image
        """
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        plt.close(fig)
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"


# For backward compatibility
from collections import defaultdict