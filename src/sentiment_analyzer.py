"""
Sentiment analysis module for GitLab review comments.

This module provides sentiment analysis capabilities using multiple algorithms,
including TextBlob and VADER, with the ability to extend to additional methods.
"""

from typing import Dict, Tuple, List, Any, Optional
from abc import ABC, abstractmethod

from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from data_models import SentimentScore


class SentimentAnalyzer:
    """Main sentiment analyzer that combines multiple algorithms."""
    
    def __init__(self):
        """Initialize the sentiment analyzer with default algorithms."""
        self.analyzers = [
            TextBlobAnalyzer(),
            VaderAnalyzer()
        ]
        self._llm_analyzer = None
    
    def analyze_sentiment(self, text: str) -> Tuple[float, Dict[str, float]]:
        """Analyze sentiment of text using multiple methods.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (TextBlob polarity, VADER scores)
        """
        # TextBlob sentiment (from first analyzer)
        textblob_sentiment = self.analyzers[0].analyze(text)
        
        # VADER sentiment (from second analyzer)
        vader_scores = self.analyzers[1].analyze(text)
        
        return textblob_sentiment, vader_scores
    
    def create_sentiment_score(self, text: str) -> SentimentScore:
        """Create a comprehensive SentimentScore object for the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentScore object with results from all analyzers
        """
        textblob_score, vader_scores = self.analyze_sentiment(text)
        
        return SentimentScore(
            textblob_score=textblob_score,
            vader_compound=vader_scores.get('compound', 0.0),
            vader_positive=vader_scores.get('pos', 0.0),
            vader_neutral=vader_scores.get('neu', 0.0),
            vader_negative=vader_scores.get('neg', 0.0)
        )
    
    def set_llm_analyzer(self, llm_analyzer: 'LLMAnalyzer'):
        """Set an LLM-based analyzer for enhanced sentiment analysis.
        
        Args:
            llm_analyzer: LLMAnalyzer instance
        """
        self._llm_analyzer = llm_analyzer
        self.analyzers.append(llm_analyzer)
    
    def enhance_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """Enhance sentiment analysis with LLM if available.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with LLM analysis results or None if LLM not available
        """
        if self._llm_analyzer:
            return self._llm_analyzer.analyze_detailed(text)
        return None


class SentimentAlgorithm(ABC):
    """Abstract base class for sentiment analysis algorithms."""
    
    @abstractmethod
    def analyze(self, text: str) -> Any:
        """Analyze the sentiment of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Algorithm-specific sentiment result
        """
        pass


class TextBlobAnalyzer(SentimentAlgorithm):
    """TextBlob-based sentiment analyzer."""
    
    def analyze(self, text: str) -> float:
        """Analyze sentiment using TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            Polarity score (-1 to 1)
        """
        blob = TextBlob(text)
        return blob.sentiment.polarity


class VaderAnalyzer(SentimentAlgorithm):
    """VADER-based sentiment analyzer."""
    
    def __init__(self):
        """Initialize the VADER analyzer."""
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with VADER scores
        """
        return self.vader.polarity_scores(text)


class LLMAnalyzer(SentimentAlgorithm):
    """LLM-based sentiment analyzer using Ollama."""
    
    def __init__(self, model: str = "llama3.2", host: Optional[str] = None):
        """Initialize the LLM analyzer.
        
        Args:
            model: Ollama model to use
            host: Ollama host URL (optional)
        """
        self.model = model
        self.host = host
        
        # Import ollama here to make it optional
        try:
            import ollama
            self.ollama = ollama
            self.available = True
        except ImportError:
            self.available = False
    
    def analyze(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using LLM.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not self.available:
            return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}
        
        try:
            # Simple prompt for sentiment score
            prompt = f"""
            Analyze this text for sentiment on a scale from -1 (very negative) to 1 (very positive):
            
            "{text}"
            
            Return only a number between -1 and 1.
            """
            
            response = self.ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            # Try to extract a number from the response
            content = response['message']['content'].strip()
            try:
                score = float(content)
                # Ensure it's in the range [-1, 1]
                score = max(-1.0, min(1.0, score))
            except ValueError:
                # Default to neutral if we can't parse a number
                score = 0.0
            
            # Convert to VADER-like format for compatibility
            if score > 0:
                pos = score
                neg = 0.0
                neu = 1.0 - pos
            else:
                neg = abs(score)
                pos = 0.0
                neu = 1.0 - neg
            
            return {
                'compound': score,
                'pos': pos,
                'neu': neu,
                'neg': neg
            }
            
        except Exception:
            # Return neutral sentiment on error
            return {'compound': 0.0, 'pos': 0.0, 'neu': 1.0, 'neg': 0.0}
    
    def analyze_detailed(self, text: str) -> Dict[str, Any]:
        """Perform detailed analysis of text using LLM.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with detailed analysis
        """
        if not self.available:
            return {
                'sentiment': 'neutral',
                'tone': 'neutral',
                'constructiveness': 'medium',
                'professionalism': 'medium',
                'analysis': 'LLM analysis unavailable'
            }
        
        try:
            prompt = f"""
            Analyze this code review comment for tone, professionalism, and sentiment:
            
            "{text}"
            
            Provide a JSON object with these fields:
            - sentiment: "positive", "neutral", or "negative"
            - tone: "supportive", "neutral", "critical", or "harsh"
            - constructiveness: "high", "medium", or "low"
            - professionalism: "high", "medium", or "low"
            - analysis: Brief 1-2 sentence analysis
            
            Return ONLY the JSON object, nothing else.
            """
            
            response = self.ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            content = response['message']['content']
            
            # Try to parse JSON from the response
            import json
            try:
                # Find JSON-like content between curly braces
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    result = json.loads(json_str)
                    return result
            except Exception:
                pass
            
            # If JSON parsing fails, return a basic analysis
            return {
                'sentiment': 'neutral',
                'tone': 'neutral',
                'constructiveness': 'medium',
                'professionalism': 'medium',
                'analysis': content[:200]  # Truncate to avoid very long responses
            }
            
        except Exception as e:
            return {
                'sentiment': 'neutral',
                'tone': 'neutral',
                'constructiveness': 'medium',
                'professionalism': 'medium',
                'analysis': f'LLM analysis failed: {str(e)[:100]}'
            }