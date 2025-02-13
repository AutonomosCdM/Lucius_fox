from typing import List, Dict, Any, Optional
from collections import Counter
from textblob import TextBlob
import re
import io

class AnalysisService:
    def __init__(self):
        self.analysis_history: List[Dict[str, Any]] = []

    async def extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text using TextBlob"""
        blob = TextBlob(text)
        sentences = blob.sentences
        
        # Score sentences based on length and word complexity
        scored_sentences = []
        for sent in sentences:
            score = len(sent.words)  # Base score on length
            score += sum(1 for word in sent.words if len(word) > 7)  # Add score for complex words
            scored_sentences.append((score, str(sent)))
        
        # Get top 5 sentences as key points
        scored_sentences.sort(reverse=True)
        return [sent for _, sent in scored_sentences[:5]]
    
    async def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate a concise summary of the text using TextBlob"""
        blob = TextBlob(text)
        sentences = blob.sentences
        
        if len(sentences) <= max_sentences:
            return text
        
        # Simple extractive summarization
        sentence_scores = []
        for sentence in sentences:
            score = len(sentence.words)  # Length-based importance
            score += sum(1 for word in sentence.words if len(word) > 7)  # Complex words
            sentence_scores.append((score, sentence))
        
        sentence_scores.sort(reverse=True)
        summary_sentences = [str(sentence) for _, sentence in sentence_scores[:max_sentences]]
        
        return ' '.join(summary_sentences)

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text and return various insights"""
        print('TextBlob input:', repr(text))
        blob = TextBlob(text)
        print('TextBlob sentences:', len(blob.sentences))
        print('TextBlob words:', len(blob.words))
        
        # Basic text analysis
        analysis = {
            'sentiment': {
                'polarity': blob.sentiment.polarity,  # -1 to 1
                'subjectivity': blob.sentiment.subjectivity,  # 0 to 1
                'assessment': 'positivo' if blob.sentiment.polarity > 0 else 'negativo' if blob.sentiment.polarity < 0 else 'neutral'
            },
            'word_count': len(blob.words),
            'sentence_count': len(blob.sentences),
            'top_words': Counter(word.lower() for word in blob.words).most_common(10)
        }
        
        self.analysis_history.append({
            'text': text[:200] + '...' if len(text) > 200 else text,
            'analysis': analysis
        })
        
        return analysis

    def get_recent_analyses(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent analysis history"""
        return self.analysis_history[-limit:]

    def clear_history(self) -> None:
        """Clear analysis history"""
        self.analysis_history = []
