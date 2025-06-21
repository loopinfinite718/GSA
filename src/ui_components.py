"""
UI/UX components and styling for advanced GitLab analysis reports.
"""
from typing import Dict, List, Any
from jinja2 import Template


class UIComponentGenerator:
    """Generates enhanced UI components for better data visualization."""
    
    def __init__(self):
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
        
        self.behavior_colors = {
            'very_supportive': '#27ae60',
            'supportive': '#2ecc71',
            'neutral': '#95a5a6',
            'critical': '#f39c12',
            'very_critical': '#e67e22',
            'potentially_toxic': '#e74c3c'
        }
    
    def create_enhanced_html_template(self) -> Template:
        """Create the advanced HTML template with modern UI/UX."""
        template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 GitLab Developer Behavior Analysis</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
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
            backdrop-filter: blur(10px);
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
        
        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 2px,
                rgba(255,255,255,0.05) 2px,
                rgba(255,255,255,0.05) 4px
            );
            animation: headerPattern 20s linear infinite;
        }
        
        @keyframes headerPattern {
            0% { transform: translateX(-50px) translateY(-50px); }
            100% { transform: translateX(0px) translateY(0px); }
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
        
        .nav-tab i {
            margin-right: 0.5rem;
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
        
        .metric-card .metric-icon {
            position: absolute;
            top: 1rem;
            right: 1rem;
            font-size: 2rem;
            opacity: 0.1;
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
        
        .metric-change {
            font-size: 0.8rem;
            margin-top: 0.5rem;
            padding: 0.2rem 0.5rem;
            border-radius: 20px;
            font-weight: 600;
        }
        
        .metric-change.positive {
            background: #d4edda;
            color: #155724;
        }
        
        .metric-change.negative {
            background: #f8d7da;
            color: #721c24;
        }
        
        .metric-change.neutral {
            background: #e2e3e5;
            color: #383d41;
        }
        
        /* Developer Analysis Section */
        .developer-selector {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: var(--border-radius);
            padding: 2rem;
            margin: 2rem 0;
            box-shadow: var(--box-shadow);
        }
        
        .developer-selector h2 {
            color: var(--primary-color);
            margin-bottom: 1rem;
        }
        
        .developer-dropdown {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 1.5rem 0;
            flex-wrap: wrap;
        }
        
        .developer-dropdown select {
            padding: 0.75rem 1rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
            min-width: 250px;
            cursor: pointer;
            transition: var(--transition);
            background: white;
        }
        
        .developer-dropdown select:focus {
            outline: none;
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }
        
        .action-button {
            padding: 0.75rem 1.5rem;
            background: var(--secondary-color);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: var(--transition);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .action-button:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }
        
        .action-button.secondary {
            background: #6c757d;
        }
        
        .action-button.secondary:hover {
            background: #5a6268;
        }
        
        /* Developer Analysis Views */
        .developer-analysis {
            display: none;
        }
        
        .developer-analysis.active {
            display: block;
        }
        
        .global-view {
            display: block;
        }
        
        .global-view.hidden {
            display: none;
        }
        
        .developer-overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .developer-card {
            background: white;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            box-shadow: var(--box-shadow);
            transition: var(--transition);
            border-top: 4px solid var(--info-color);
        }
        
        .developer-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .developer-card h4 {
            color: var(--primary-color);
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }
        
        .developer-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 0.5rem;
            background: #f8f9fa;
            border-radius: 6px;
        }
        
        .stat-value {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--primary-color);
        }
        
        .stat-label {
            font-size: 0.8rem;
            color: #666;
            margin-top: 0.2rem;
        }
        
        /* Treatment Analysis */
        .reviewer-treatment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }
        
        .reviewer-treatment {
            background: white;
            border-radius: 8px;
            padding: 1.2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: var(--transition);
        }
        
        .reviewer-treatment:hover {
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        
        .treatment-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .reviewer-name {
            font-weight: 600;
            color: var(--primary-color);
        }
        
        .treatment-badge {
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .treatment-very-supportive { background: #27ae60; }
        .treatment-supportive { background: #2ecc71; }
        .treatment-neutral { background: #95a5a6; }
        .treatment-critical { background: #f39c12; }
        .treatment-very-critical { background: #e67e22; }
        .treatment-potentially-toxic { background: #e74c3c; }
        
        .treatment-metrics {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
        }
        
        .treatment-metric {
            font-size: 0.85rem;
            color: #666;
        }
        
        .treatment-metric strong {
            color: var(--primary-color);
        }
        
        /* Risk Indicators */
        .risk-indicator {
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .risk-low {
            background: #d4edda;
            color: #155724;
        }
        
        .risk-medium {
            background: #fff3cd;
            color: #856404;
        }
        
        .risk-high {
            background: #f8d7da;
            color: #721c24;
        }
        
        /* Bias Analysis */
        .bias-alert {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 2px solid #f39c12;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin: 1.5rem 0;
        }
        
        .bias-alert h3 {
            color: #856404;
            margin-bottom: 1rem;
        }
        
        .bias-indicators {
            list-style: none;
            padding: 0;
        }
        
        .bias-indicators li {
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(133, 100, 4, 0.2);
        }
        
        .bias-indicators li:last-child {
            border-bottom: none;
        }
        
        .bias-indicators li::before {
            content: '⚠️';
            margin-right: 0.5rem;
        }
        
        /* Recommendations */
        .recommendations {
            background: #d1ecf1;
            border: 2px solid #bee5eb;
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin: 1.5rem 0;
        }
        
        .recommendations h3 {
            color: #0c5460;
            margin-bottom: 1rem;
        }
        
        .recommendations ul {
            list-style: none;
            padding: 0;
        }
        
        .recommendations li {
            padding: 0.5rem 0;
            color: #0c5460;
        }
        
        .recommendations li::before {
            content: '💡';
            margin-right: 0.5rem;
        }
        
        /* Charts Container */
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
        
        /* Loading States */
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
            color: #666;
        }
        
        .loading::after {
            content: '';
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid var(--secondary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
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
            
            .developer-overview-grid {
                grid-template-columns: 1fr;
            }
            
            .reviewer-treatment-grid {
                grid-template-columns: 1fr;
            }
            
            .content {
                padding: 1.5rem;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #ecf0f1;
                --light-bg: #2c3e50;
            }
            
            body {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            }
        }
        
        /* Accessibility */
        .nav-tab:focus,
        .action-button:focus,
        .developer-dropdown select:focus {
            outline: 2px solid var(--secondary-color);
            outline-offset: 2px;
        }
        
        /* Print styles */
        @media print {
            body {
                background: white;
            }
            
            .main-container {
                box-shadow: none;
            }
            
            .nav-container {
                display: none;
            }
            
            .tab-content {
                display: block !important;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- Header -->
        <header class="header">
            <h1><i class="fas fa-search"></i> GitLab Developer Behavior Analysis</h1>
            <div class="subtitle">
                <i class="fas fa-calendar"></i> Generated on {{ generated_at }} | 
                <i class="fas fa-clock"></i> Period: {{ analysis_period }} | 
                <i class="fas fa-code-branch"></i> Total MRs: {{ total_mrs }}
            </div>
        </header>

        <!-- Navigation -->
        <nav class="nav-container">
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('overview')">
                    <i class="fas fa-chart-line"></i> Overview
                </button>
                <button class="nav-tab" onclick="showTab('behavior')">
                    <i class="fas fa-user-shield"></i> Behavior Patterns
                </button>
                <button class="nav-tab" onclick="showTab('developers')">
                    <i class="fas fa-users"></i> Developer Analysis
                </button>
                <button class="nav-tab" onclick="showTab('bias')">
                    <i class="fas fa-exclamation-triangle"></i> Bias Detection
                </button>
                <button class="nav-tab" onclick="showTab('team')">
                    <i class="fas fa-sitemap"></i> Team Dynamics
                </button>
            </div>
        </nav>

        <!-- Content -->
        <main class="content">
            <!-- Overview Tab -->
            <section id="overview" class="tab-content active">
                <h2><i class="fas fa-chart-pie"></i> Executive Summary</h2>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-comments"></i></div>
                        <div class="metric-value">{{ summary.total_reviews }}</div>
                        <div class="metric-label">Total Reviews</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-heart"></i></div>
                        <div class="metric-value">{{ "%.3f"|format(summary.avg_sentiment) }}</div>
                        <div class="metric-label">Average Sentiment</div>
                        <div class="metric-change {{ 'positive' if summary.avg_sentiment > 0 else 'negative' if summary.avg_sentiment < 0 else 'neutral' }}">
                            {{ summary.sentiment_comparison }} than team avg
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-shield-alt"></i></div>
                        <div class="metric-value risk-{{ summary.bias_risk_level.lower() }}">{{ summary.bias_risk_level }}</div>
                        <div class="metric-label">Bias Risk Level</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-chat-dots"></i></div>
                        <div class="metric-value">{{ summary.communication_style }}</div>
                        <div class="metric-label">Communication Style</div>
                    </div>
                </div>

                <div class="chart-container">
                    <div class="chart-title">Key Insights</div>
                    {% for pattern in advanced_insights.patterns %}
                    <div class="metric-card">
                        <i class="fas fa-lightbulb" style="color: var(--warning-color); margin-right: 0.5rem;"></i>
                        {{ pattern }}
                    </div>
                    {% endfor %}
                </div>
            </section>

            <!-- Behavior Patterns Tab -->
            <section id="behavior" class="tab-content">
                <h2><i class="fas fa-user-shield"></i> Negative Behavior Pattern Analysis</h2>
                
                <div class="chart-container">
                    <div class="chart-title">Communication Pattern Breakdown</div>
                    <div class="metrics-grid">
                        {% for sentiment_type, percentage in communication_patterns.sentiment_distribution.items() %}
                        <div class="metric-card">
                            <div class="metric-value">{{ "%.1f"|format(percentage * 100) }}%</div>
                            <div class="metric-label">{{ sentiment_type.replace('_', ' ')|title }}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                {% if advanced_insights.risk_factors %}
                <div class="bias-alert">
                    <h3><i class="fas fa-exclamation-triangle"></i> Risk Factors Identified</h3>
                    <ul class="bias-indicators">
                        {% for risk in advanced_insights.risk_factors %}
                        <li>{{ risk }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}

                {% if advanced_insights.recommendations %}
                <div class="recommendations">
                    <h3><i class="fas fa-lightbulb"></i> Improvement Recommendations</h3>
                    <ul>
                        {% for recommendation in advanced_insights.recommendations %}
                        <li>{{ recommendation }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </section>

            <!-- Developer Analysis Tab -->
            <section id="developers" class="tab-content">
                <div class="developer-selector">
                    <h2><i class="fas fa-user-magnifying-glass"></i> Individual Developer Treatment Analysis</h2>
                    <p>Analyze how each developer is treated by different reviewers to identify potential bias, harassment, or unfair treatment patterns.</p>
                    
                    <div class="developer-dropdown">
                        <label for="developerSelect"><strong>Select Developer:</strong></label>
                        <select id="developerSelect" onchange="showDeveloperAnalysis()">
                            <option value="">-- Choose a Developer --</option>
                            {% for developer in developer_analysis.keys() %}
                            <option value="{{ developer }}">{{ developer }}</option>
                            {% endfor %}
                        </select>
                        <button class="action-button secondary" onclick="showGlobalView()" id="backButton" style="display: none;">
                            <i class="fas fa-arrow-left"></i> Back to Overview
                        </button>
                    </div>
                </div>
                
                <!-- Global Developer Overview -->
                <div id="globalView" class="global-view">
                    <h3><i class="fas fa-globe"></i> Team-wide Developer Treatment Overview</h3>
                    <div class="developer-overview-grid">
                        {% for developer, dev_analysis in developer_analysis.items() %}
                        <div class="developer-card">
                            <h4><i class="fas fa-user"></i> {{ developer }}</h4>
                            
                            <div class="developer-stats">
                                <div class="stat-item">
                                    <div class="stat-value">{{ "%.3f"|format(dev_analysis.overall_sentiment) }}</div>
                                    <div class="stat-label">Avg Sentiment</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value">{{ dev_analysis.total_reviews }}</div>
                                    <div class="stat-label">Total Reviews</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-value risk-{{ dev_analysis.bias_risk }}">{{ dev_analysis.bias_risk|title }}</div>
                                    <div class="stat-label">Bias Risk</div>
                                </div>
                            </div>
                            
                            {% if dev_analysis.bias_indicators %}
                            <div class="bias-alert" style="margin-top: 1rem;">
                                <h4>⚠️ Concerns Detected</h4>
                                <ul style="margin: 0.5rem 0; padding-left: 1rem;">
                                    {% for indicator in dev_analysis.bias_indicators %}
                                    <li style="font-size: 0.85rem;">{{ indicator }}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <!-- Individual Developer Analysis -->
                {% for developer, dev_analysis in developer_analysis.items() %}
                <div id="developer-{{ developer|replace(' ', '-') }}" class="developer-analysis">
                    <h3><i class="fas fa-user-circle"></i> Detailed Analysis: {{ developer }}</h3>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-heart"></i></div>
                            <div class="metric-value">{{ "%.3f"|format(dev_analysis.overall_sentiment) }}</div>
                            <div class="metric-label">Overall Sentiment</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-comments"></i></div>
                            <div class="metric-value">{{ dev_analysis.total_reviews }}</div>
                            <div class="metric-label">Total Reviews</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                            <div class="metric-value">{{ "%.3f"|format(dev_analysis.sentiment_range) }}</div>
                            <div class="metric-label">Sentiment Range</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-shield-alt"></i></div>
                            <div class="metric-value risk-{{ dev_analysis.bias_risk }}">{{ dev_analysis.bias_risk|title }}</div>
                            <div class="metric-label">Bias Risk</div>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-title">👥 Treatment by Individual Reviewers</div>
                        <div class="reviewer-treatment-grid">
                            {% for reviewer, stats in dev_analysis.reviewer_stats.items() %}
                            <div class="reviewer-treatment">
                                <div class="treatment-header">
                                    <div class="reviewer-name">{{ reviewer }}</div>
                                    <span class="treatment-badge treatment-{{ stats.treatment.lower().replace(' ', '-') }}">
                                        {{ stats.treatment_icon }} {{ stats.treatment }}
                                    </span>
                                </div>
                                <div class="treatment-metrics">
                                    <div class="treatment-metric">
                                        <strong>Sentiment:</strong> {{ "%.3f"|format(stats.avg_sentiment) }}
                                    </div>
                                    <div class="treatment-metric">
                                        <strong>Reviews:</strong> {{ stats.review_count }}
                                    </div>
                                    <div class="treatment-metric">
                                        <strong>Approval Rate:</strong> {{ "%.1f"|format(stats.approval_rate * 100) }}%
                                    </div>
                                    <div class="treatment-metric">
                                        <strong>Change Requests:</strong> {{ "%.1f"|format(stats.change_request_rate * 100) }}%
                                    </div>
                                </div>
                                
                                {% if stats.negative_patterns %}
                                <div style="margin-top: 1rem; padding: 0.5rem; background: #f8d7da; border-radius: 4px;">
                                    <strong style="color: #721c24;">Negative Patterns:</strong>
                                    <ul style="margin: 0.5rem 0; padding-left: 1rem; font-size: 0.8rem;">
                                        {% for pattern in stats.negative_patterns %}
                                        <li style="color: #721c24;">{{ pattern }}</li>
                                        {% endfor %}
                                    </ul>
                                </div>
                                {% endif %}
                                
                                <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #666;">
                                    <strong>Communication Style:</strong> {{ stats.communication_style }}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    {% if dev_analysis.recommendations %}
                    <div class="recommendations">
                        <h3><i class="fas fa-lightbulb"></i> Recommendations for {{ developer }}</h3>
                        <ul>
                            {% for recommendation in dev_analysis.recommendations %}
                            <li>{{ recommendation }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </section>

            <!-- Bias Detection Tab -->
            <section id="bias" class="tab-content">
                <h2><i class="fas fa-exclamation-triangle"></i> Bias Risk Analysis</h2>
                
                <div class="bias-alert">
                    <h3>Overall Assessment</h3>
                    <p><strong>Risk Level:</strong> <span class="risk-indicator risk-{{ bias_analysis.overall_risk }}">{{ bias_analysis.overall_risk|title }}</span></p>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Author-Specific Analysis</div>
                    <div class="metrics-grid">
                        {% for author, analysis in bias_analysis.author_analysis.items() %}
                        <div class="metric-card">
                            <h4>{{ author }}</h4>
                            <div class="stat-item">
                                <div class="stat-value">{{ "%.3f"|format(analysis.avg_sentiment) }}</div>
                                <div class="stat-label">Average Sentiment</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">{{ analysis.review_count }}</div>
                                <div class="stat-label">Review Count</div>
                            </div>
                            <div class="risk-indicator risk-{{ analysis.risk_level }}">{{ analysis.risk_level|title }} Risk</div>
                            {% if analysis.patterns %}
                            <div style="margin-top: 0.5rem; font-size: 0.8rem;">
                                <strong>Patterns:</strong> {{ analysis.patterns|join(", ") }}
                            </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                {% if bias_analysis.mitigation_strategies %}
                <div class="recommendations">
                    <h3><i class="fas fa-tools"></i> Recommended Actions</h3>
                    <ul>
                        {% for strategy in bias_analysis.mitigation_strategies %}
                        <li>{{ strategy }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </section>

            <!-- Team Dynamics Tab -->
            <section id="team" class="tab-content">
                <h2><i class="fas fa-sitemap"></i> Team Dynamics Analysis</h2>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-users"></i></div>
                        <div class="metric-value">{{ "%.1f"|format(team_dynamics.team_cohesion) }}</div>
                        <div class="metric-label">Team Cohesion Score</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-comment"></i></div>
                        <div class="metric-value">{{ "%.0f"|format(communication_patterns.average_comment_length) }}</div>
                        <div class="metric-label">Avg Comment Length (chars)</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Communication Pattern Distribution</div>
                    <div class="metrics-grid">
                        {% for sentiment_type, percentage in communication_patterns.sentiment_distribution.items() %}
                        <div class="metric-card">
                            <div class="metric-value">{{ "%.1f"|format(percentage * 100) }}%</div>
                            <div class="metric-label">{{ sentiment_type.replace('_', ' ')|title }}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                {% if advanced_insights.recommendations %}
                <div class="recommendations">
                    <h3><i class="fas fa-target"></i> Team Improvement Recommendations</h3>
                    <ul>
                        {% for recommendation in advanced_insights.recommendations %}
                        <li>{{ recommendation }}</li>
                        {% endfor %}
                        {% if not advanced_insights.recommendations %}
                        <li>Current review practices show healthy patterns</li>
                        <li>Continue maintaining balanced communication</li>
                        <li>Consider periodic review of team dynamics</li>
                        {% endif %}
                    </ul>
                </div>
                {% endif %}
            </section>
        </main>
    </div>

    <script>
        function showTab(tabId) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.nav-tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            const selectedTab = document.getElementById(tabId);
            if (selectedTab) selectedTab.classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }
        
        function showDeveloperAnalysis() {
            const select = document.getElementById('developerSelect');
            const selectedDeveloper = select.value;
            
            // Hide global view
            const globalView = document.getElementById('globalView');
            if (globalView) globalView.classList.add('hidden');
            
            // Hide all developer analyses
            const allAnalyses = document.querySelectorAll('.developer-analysis');
            allAnalyses.forEach(analysis => analysis.classList.remove('active'));
            
            if (selectedDeveloper) {
                // Show selected developer analysis
                const developerId = selectedDeveloper.replace(/ /g, '-');
                const developerDiv = document.getElementById('developer-' + developerId);
                if (developerDiv) {
                    developerDiv.classList.add('active');
                }
                
                // Show back button
                const backButton = document.getElementById('backButton');
                if (backButton) backButton.style.display = 'inline-flex';
            } else {
                showGlobalView();
            }
        }
        
        function showGlobalView() {
            // Show global view
            const globalView = document.getElementById('globalView');
            if (globalView) globalView.classList.remove('hidden');
            
            // Hide all developer analyses
            const allAnalyses = document.querySelectorAll('.developer-analysis');
            allAnalyses.forEach(analysis => analysis.classList.remove('active'));
            
            // Hide back button
            const backButton = document.getElementById('backButton');
            if (backButton) backButton.style.display = 'none';
            
            // Reset dropdown
            const select = document.getElementById('developerSelect');
            if (select) select.value = '';
        }
        
        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Advanced GitLab Review Analysis Report loaded');
            
            // Add keyboard navigation
            document.addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key >= '1' && e.key <= '5') {
                    e.preventDefault();
                    const tabIndex = parseInt(e.key) - 1;
                    const tabs = document.querySelectorAll('.nav-tab');
                    if (tabs[tabIndex]) {
                        tabs[tabIndex].click();
                    }
                }
            });
        });
    </script>
</body>
</html>
        '''
        
        return Template(template_str)
    
    def generate_behavior_insights_component(self, behavior_data: Dict) -> str:
        """Generate behavior insights component HTML."""
        insights_html = "<div class='behavior-insights'>"
        
        for pattern_type, patterns in behavior_data.items():
            insights_html += f"<div class='pattern-section'>"
            insights_html += f"<h4>{pattern_type.replace('_', ' ').title()}</h4>"
            for pattern in patterns:
                severity_class = f"severity-{pattern.get('severity', 'low')}"
                insights_html += f"<div class='pattern-item {severity_class}'>"
                insights_html += f"<strong>{pattern.get('description', '')}</strong>"
                insights_html += f"<span class='frequency'>Frequency: {pattern.get('frequency', 0)}</span>"
                insights_html += "</div>"
            insights_html += "</div>"
        
        insights_html += "</div>"
        return insights_html
    
    def generate_risk_badge(self, risk_level: str) -> str:
        """Generate a risk level badge."""
        color_map = {
            'low': self.colors['success'],
            'medium': self.colors['warning'],
            'high': self.colors['danger']
        }
        
        return f"""
        <span class="risk-badge" style="background-color: {color_map.get(risk_level, '#666')}; 
              color: white; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.8rem;">
            {risk_level.upper()}
        </span>
        """
    
    def generate_treatment_visualization(self, treatment_data: Dict) -> str:
        """Generate treatment pattern visualization."""
        viz_html = "<div class='treatment-visualization'>"
        
        for reviewer, data in treatment_data.items():
            treatment_level = data.get('treatment', 'neutral')
            color = self.behavior_colors.get(treatment_level.lower().replace(' ', '_'), '#666')
            
            viz_html += f"""
            <div class='reviewer-card' style='border-left: 4px solid {color}'>
                <h5>{reviewer}</h5>
                <div class='treatment-metrics'>
                    <span>Sentiment: {data.get('avg_sentiment', 0):.3f}</span>
                    <span>Reviews: {data.get('review_count', 0)}</span>
                </div>
                <div class='treatment-badge' style='background: {color}'>
                    {treatment_level}
                </div>
            </div>
            """
        
        viz_html += "</div>"
        return viz_html
