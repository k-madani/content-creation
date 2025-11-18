import requests
from bs4 import BeautifulSoup
import textstat
import re
from typing import Dict
from utils.error_handler import handle_errors


class ToneAnalyzerTool:
    """
    Custom tool for analyzing writing tone and style
    """
    
    name: str = "Tone Analyzer"
    description: str = """Analyzes writing style and tone from provided text or URLs.
    Extracts metrics like formality, readability, sentence structure, and generates
    style guidelines that can be used to match a specific writing tone."""

    @handle_errors(error_message="Tone analysis failed")
    def run(self, content: str) -> str:
        """
        Analyze tone and style from content
        
        Args:
            content: Either a URL starting with 'http' or raw text
            
        Returns:
            Detailed tone analysis with style guidelines
        """
        # Check if input is URL or text
        if content.startswith('http'):
            text = self._fetch_content_from_url(content)
        else:
            text = content
        
        if not text or len(text) < 100:
            return "Error: Content too short for meaningful analysis (need at least 100 characters)"
        
        # Perform analysis
        analysis = self._analyze_text(text)
        
        # Generate style guidelines
        guidelines = self._generate_style_guidelines(analysis)
        
        return self._format_results(analysis, guidelines)
    
    def _fetch_content_from_url(self, url: str) -> str:
        """Fetch and extract text content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text from paragraphs
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to fetch URL content: {str(e)}")
    
    def _analyze_text(self, text: str) -> Dict:
        """Perform comprehensive text analysis"""
        
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into sentences and words
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        # Calculate metrics
        analysis = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            
            # Readability scores
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            
            # Complexity
            'difficult_words': textstat.difficult_words(text),
            'complex_word_percentage': (textstat.difficult_words(text) / len(words) * 100) if words else 0,
            
            # Structure analysis
            'short_sentences': sum(1 for s in sentences if len(s.split()) < 10),
            'medium_sentences': sum(1 for s in sentences if 10 <= len(s.split()) <= 20),
            'long_sentences': sum(1 for s in sentences if len(s.split()) > 20),
            
            # Style markers
            'question_count': text.count('?'),
            'exclamation_count': text.count('!'),
            'uses_contractions': bool(re.search(r"\b\w+'\w+\b", text)),
            'uses_first_person': bool(re.search(r'\b(I|we|my|our)\b', text, re.IGNORECASE)),
            'uses_second_person': bool(re.search(r'\b(you|your)\b', text, re.IGNORECASE)),
        }
        
        return analysis
    
    def _generate_style_guidelines(self, analysis: Dict) -> Dict:
        """Generate actionable style guidelines based on analysis"""
        
        guidelines = {}
        
        # Determine formality level
        formality_score = 0
        if not analysis['uses_contractions']:
            formality_score += 2
        if not analysis['uses_first_person']:
            formality_score += 2
        if analysis['avg_word_length'] > 5:
            formality_score += 2
        if analysis['avg_sentence_length'] > 20:
            formality_score += 2
        if analysis['complex_word_percentage'] > 15:
            formality_score += 2
        
        if formality_score >= 7:
            guidelines['formality'] = 'Highly Formal'
            guidelines['formality_instruction'] = 'Use formal language, avoid contractions, use third-person perspective, prefer longer sentences and sophisticated vocabulary.'
        elif formality_score >= 4:
            guidelines['formality'] = 'Professional'
            guidelines['formality_instruction'] = 'Maintain professional tone, use clear language, balanced sentence length, occasional contractions acceptable.'
        else:
            guidelines['formality'] = 'Casual/Conversational'
            guidelines['formality_instruction'] = 'Use conversational tone, contractions welcome, first and second person acceptable, shorter sentences preferred.'
        
        # Reading level
        grade = analysis['flesch_kincaid_grade']
        if grade <= 8:
            guidelines['reading_level'] = 'Easy (General Public)'
            guidelines['reading_instruction'] = 'Write for general audience, use simple words, short sentences, clear explanations.'
        elif grade <= 12:
            guidelines['reading_level'] = 'Moderate (High School)'
            guidelines['reading_instruction'] = 'Write for educated audience, moderate complexity acceptable, explain technical terms.'
        else:
            guidelines['reading_level'] = 'Advanced (College+)'
            guidelines['reading_instruction'] = 'Write for expert audience, technical terminology acceptable, complex concepts expected.'
        
        # Sentence structure
        if analysis['avg_sentence_length'] < 15:
            guidelines['sentence_style'] = 'Short and punchy'
            guidelines['sentence_instruction'] = 'Keep sentences brief (10-15 words average), use active voice, direct statements.'
        elif analysis['avg_sentence_length'] < 25:
            guidelines['sentence_style'] = 'Balanced'
            guidelines['sentence_instruction'] = 'Mix short and medium sentences (15-25 words average), vary structure for rhythm.'
        else:
            guidelines['sentence_style'] = 'Long and detailed'
            guidelines['sentence_instruction'] = 'Use longer, more complex sentences (25+ words), include clauses and detailed explanations.'
        
        # Engagement style
        engagement_features = []
        if analysis['question_count'] > 0:
            engagement_features.append('rhetorical questions')
        if analysis['uses_second_person']:
            engagement_features.append('direct address to reader')
        if analysis['exclamation_count'] > 0:
            engagement_features.append('emphatic statements')
        
        if engagement_features:
            guidelines['engagement'] = 'Interactive'
            guidelines['engagement_instruction'] = f"Engage readers using: {', '.join(engagement_features)}."
        else:
            guidelines['engagement'] = 'Informative'
            guidelines['engagement_instruction'] = 'Focus on clear information delivery, straightforward statements.'
        
        return guidelines
    
    def _format_results(self, analysis: Dict, guidelines: Dict) -> str:
        """Format analysis results as readable text"""
        
        result = """
TONE ANALYSIS RESULTS
=====================

CONTENT METRICS:
- Total Words: {word_count}
- Total Sentences: {sentence_count}
- Average Sentence Length: {avg_sentence_length:.1f} words
- Average Word Length: {avg_word_length:.1f} characters

READABILITY:
- Flesch Reading Ease: {flesch_reading_ease:.1f} (0-100, higher = easier)
- Grade Level: {flesch_kincaid_grade:.1f}
- Complex Words: {difficult_words} ({complex_word_percentage:.1f}%)

STYLE CHARACTERISTICS:
- Short Sentences (<10 words): {short_sentences}
- Medium Sentences (10-20 words): {medium_sentences}
- Long Sentences (>20 words): {long_sentences}
- Uses Contractions: {uses_contractions}
- Uses First Person: {uses_first_person}
- Uses Second Person: {uses_second_person}
- Questions: {question_count}
- Exclamations: {exclamation_count}

TONE PROFILE:
- Formality: {formality}
- Reading Level: {reading_level}
- Sentence Style: {sentence_style}
- Engagement: {engagement}

STYLE GUIDELINES FOR WRITING:
================================
{formality_instruction}

{reading_instruction}

{sentence_instruction}

{engagement_instruction}

RECOMMENDED APPROACH:
Write content that matches this tone profile. {formality} style with {sentence_style} sentences 
targeting {reading_level} audience. {engagement} approach to reader engagement.
""".format(
            **analysis,
            formality=guidelines['formality'],
            formality_instruction=guidelines['formality_instruction'],
            reading_level=guidelines['reading_level'],
            reading_instruction=guidelines['reading_instruction'],
            sentence_style=guidelines['sentence_style'],
            sentence_instruction=guidelines['sentence_instruction'],
            engagement=guidelines['engagement'],
            engagement_instruction=guidelines['engagement_instruction']
        )
        
        return result