"""
Tone Analyzer Tool - Updated for CrewAI 1.5.0+
Analyzes writing style and tone
"""

import requests
from bs4 import BeautifulSoup
import textstat
import re
from typing import Dict
from crewai.tools import tool


@tool("Tone Analyzer")
def tone_analyzer(content: str, target_tone: str = "professional") -> str:
    """
    Analyzes writing style and tone from provided text or URLs.
    Extracts metrics like formality, readability, sentence structure, and generates
    style guidelines that can be used to match a specific writing tone.
    
    Args:
        content: Either a URL starting with 'http' or raw text to analyze
        target_tone: Target tone to match (e.g., professional, casual, formal)
        
    Returns:
        Detailed tone analysis with style guidelines
    """
    try:
        # Check if input is URL or text
        if content.startswith('http'):
            text = _fetch_content_from_url(content)
        else:
            text = content
        
        if not text or len(text) < 100:
            return "Error: Content too short for meaningful analysis (need at least 100 characters)"
        
        # Perform analysis
        analysis = _analyze_text(text)
        
        # Generate style guidelines
        guidelines = _generate_style_guidelines(analysis, target_tone)
        
        return _format_results(analysis, guidelines)
        
    except Exception as e:
        return f"Tone analysis failed: {str(e)}"


def _fetch_content_from_url(url: str) -> str:
    """Fetch and extract text content from URL"""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
    
    paragraphs = soup.find_all('p')
    text = ' '.join([p.get_text() for p in paragraphs])
    return text.strip()


def _analyze_text(text: str) -> Dict:
    """Perform comprehensive text analysis"""
    
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    
    try:
        flesch_score = textstat.flesch_reading_ease(text)
        grade_level = textstat.flesch_kincaid_grade(text)
        difficult_words_count = textstat.difficult_words(text)
    except:
        flesch_score = 50.0
        grade_level = 10.0
        difficult_words_count = int(len(words) * 0.15)
    
    analysis = {
        'word_count': len(words),
        'sentence_count': len(sentences),
        'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
        'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
        'flesch_reading_ease': flesch_score,
        'flesch_kincaid_grade': grade_level,
        'difficult_words': difficult_words_count,
        'complex_word_percentage': (difficult_words_count / len(words) * 100) if words else 0,
        'short_sentences': sum(1 for s in sentences if len(s.split()) < 10),
        'medium_sentences': sum(1 for s in sentences if 10 <= len(s.split()) <= 20),
        'long_sentences': sum(1 for s in sentences if len(s.split()) > 20),
        'question_count': text.count('?'),
        'exclamation_count': text.count('!'),
        'uses_contractions': bool(re.search(r"\b\w+'\w+\b", text)),
        'uses_first_person': bool(re.search(r'\b(I|we|my|our)\b', text, re.IGNORECASE)),
        'uses_second_person': bool(re.search(r'\b(you|your)\b', text, re.IGNORECASE)),
    }
    
    return analysis


def _generate_style_guidelines(analysis: Dict, target_tone: str) -> Dict:
    """Generate style guidelines based on analysis"""
    
    guidelines = {}
    
    # Determine formality
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
    elif formality_score >= 4:
        guidelines['formality'] = 'Professional'
    else:
        guidelines['formality'] = 'Casual/Conversational'
    
    # Reading level
    grade = analysis['flesch_kincaid_grade']
    if grade <= 8:
        guidelines['reading_level'] = 'Easy (General Public)'
    elif grade <= 12:
        guidelines['reading_level'] = 'Moderate (High School)'
    else:
        guidelines['reading_level'] = 'Advanced (College+)'
    
    # Sentence style
    if analysis['avg_sentence_length'] < 15:
        guidelines['sentence_style'] = 'Short and punchy'
    elif analysis['avg_sentence_length'] < 25:
        guidelines['sentence_style'] = 'Balanced'
    else:
        guidelines['sentence_style'] = 'Long and detailed'
    
    # Engagement
    engagement_features = []
    if analysis['question_count'] > 0:
        engagement_features.append('questions')
    if analysis['uses_second_person']:
        engagement_features.append('direct address')
    if analysis['exclamation_count'] > 0:
        engagement_features.append('emphasis')
    
    guidelines['engagement'] = 'Interactive' if engagement_features else 'Informative'
    guidelines['target_tone'] = target_tone
    
    return guidelines


def _format_results(analysis: Dict, guidelines: Dict) -> str:
    """Format analysis results"""
    
    result = f"""
TONE ANALYSIS RESULTS
=====================

CONTENT METRICS:
- Total Words: {analysis['word_count']}
- Total Sentences: {analysis['sentence_count']}
- Average Sentence Length: {analysis['avg_sentence_length']:.1f} words

READABILITY:
- Flesch Reading Ease: {analysis['flesch_reading_ease']:.1f}
- Grade Level: {analysis['flesch_kincaid_grade']:.1f}
- Complex Words: {analysis['difficult_words']} ({analysis['complex_word_percentage']:.1f}%)

STYLE:
- Formality: {guidelines['formality']}
- Reading Level: {guidelines['reading_level']}
- Sentence Style: {guidelines['sentence_style']}
- Engagement: {guidelines['engagement']}
- Uses Contractions: {analysis['uses_contractions']}
- Uses First Person: {analysis['uses_first_person']}

TARGET: {guidelines['target_tone']}
"""
    
    return result