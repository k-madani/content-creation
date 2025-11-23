"""
SEO Optimizer Tool - Updated for CrewAI 1.5.0+
Analyzes content for SEO effectiveness
"""

import re
import textstat
from typing import Dict, List
from collections import Counter
from crewai.tools import tool


@tool("SEO Optimizer")
def seo_optimizer(content: str, target_keyword: str = None) -> str:
    """
    Analyzes content for SEO effectiveness and provides optimization recommendations.
    Includes keyword analysis, readability scoring, and SEO best practices.
    
    Args:
        content: The blog post content to analyze
        target_keyword: Optional primary keyword to optimize for
        
    Returns:
        SEO analysis report with recommendations
    """
    try:
        if not content or len(content) < 100:
            return "Error: Content too short for SEO analysis (need at least 100 characters)"
        
        # Perform SEO analysis
        seo_metrics = _analyze_seo(content, target_keyword)
        
        # Generate recommendations
        recommendations = _generate_recommendations(seo_metrics)
        
        return _format_results(seo_metrics, recommendations)
        
    except Exception as e:
        return f"SEO analysis failed: {str(e)}"


def _analyze_seo(content: str, target_keyword: str = None) -> Dict:
    """Perform comprehensive SEO analysis"""
    
    # Clean and prepare text
    text = re.sub(r'\s+', ' ', content).strip()
    text_lower = text.lower()
    
    # Extract words
    words = re.findall(r'\b[a-z]+\b', text_lower)
    word_count = len(words)
    
    # Extract sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Extract headers (markdown format)
    headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
    h1_headers = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
    h2_headers = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    
    # Keyword analysis
    keyword_metrics = {}
    if target_keyword:
        keyword_lower = target_keyword.lower()
        keyword_count = text_lower.count(keyword_lower)
        keyword_density = (keyword_count / word_count * 100) if word_count > 0 else 0
        
        # Check keyword placement
        in_title = keyword_lower in (h1_headers[0].lower() if h1_headers else "")
        in_first_paragraph = keyword_lower in text_lower[:500]
        in_headers = any(keyword_lower in h.lower() for h in headers)
        
        keyword_metrics = {
            'target_keyword': target_keyword,
            'keyword_count': keyword_count,
            'keyword_density': keyword_density,
            'in_title': in_title,
            'in_first_paragraph': in_first_paragraph,
            'in_headers': in_headers
        }
    
    # Get most common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                  'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
                  'it', 'its', 'you', 'your', 'they', 'their', 'we', 'our'}
    
    filtered_words = [w for w in words if w not in stop_words and len(w) > 3]
    word_freq = Counter(filtered_words)
    top_keywords = word_freq.most_common(10)
    
    # Readability metrics
    try:
        flesch_score = textstat.flesch_reading_ease(text)
        grade_level = textstat.flesch_kincaid_grade(text)
    except:
        flesch_score = 50.0
        grade_level = 10.0
    
    # Calculate readability rating
    if flesch_score >= 60:
        readability_rating = "Good"
    elif flesch_score >= 50:
        readability_rating = "Acceptable"
    else:
        readability_rating = "Difficult"
    
    # Content structure analysis
    has_title = len(h1_headers) > 0
    has_subheaders = len(h2_headers) >= 3
    
    # Link analysis
    internal_links = len(re.findall(r'\[([^\]]+)\]\((?!http)', content))
    external_links = len(re.findall(r'\[([^\]]+)\]\(http', content))
    
    # Meta description
    meta_description = re.search(r'<!-- meta: (.+) -->', content)
    has_meta = meta_description is not None
    
    # Compile metrics
    metrics = {
        'word_count': word_count,
        'sentence_count': len(sentences),
        'avg_sentence_length': word_count / len(sentences) if sentences else 0,
        'flesch_reading_ease': flesch_score,
        'grade_level': grade_level,
        'readability_rating': readability_rating,
        'h1_count': len(h1_headers),
        'h2_count': len(h2_headers),
        'total_headers': len(headers),
        'has_proper_title': has_title,
        'has_subheaders': has_subheaders,
        'internal_links': internal_links,
        'external_links': external_links,
        'has_meta_description': has_meta,
        'top_keywords': top_keywords[:5],
        **keyword_metrics
    }
    
    return metrics


def _generate_recommendations(metrics: Dict) -> List[str]:
    """Generate actionable SEO recommendations"""
    
    recommendations = []
    
    # Word count
    if metrics['word_count'] < 300:
        recommendations.append("CRITICAL: Content too short. Aim for 800-1500 words for better SEO.")
    elif metrics['word_count'] < 800:
        recommendations.append("Consider expanding content to 800-1500 words for optimal SEO.")
    
    # Readability
    if metrics['flesch_reading_ease'] < 50:
        recommendations.append("Improve readability: Use shorter sentences and simpler words.")
    
    # Headers
    if not metrics['has_proper_title']:
        recommendations.append("CRITICAL: Add a clear H1 title at the beginning.")
    if metrics['h1_count'] > 1:
        recommendations.append("Use only one H1 header. Use H2, H3 for subheadings.")
    if not metrics['has_subheaders']:
        recommendations.append("Add more H2 subheaders (aim for 3-5) to improve structure.")
    
    # Keywords
    if 'target_keyword' in metrics:
        if metrics['keyword_density'] < 0.5:
            recommendations.append(f"Increase '{metrics['target_keyword']}' usage. Current density: {metrics['keyword_density']:.1f}%")
        elif metrics['keyword_density'] > 2.5:
            recommendations.append(f"Reduce '{metrics['target_keyword']}' usage. Current: {metrics['keyword_density']:.1f}%")
        
        if not metrics['in_title']:
            recommendations.append(f"Include '{metrics['target_keyword']}' in the H1 title.")
        if not metrics['in_first_paragraph']:
            recommendations.append(f"Include '{metrics['target_keyword']}' in the first paragraph.")
    
    # Links
    if metrics['internal_links'] == 0:
        recommendations.append("Add internal links to related content.")
    if metrics['external_links'] == 0:
        recommendations.append("Add 2-3 external links to authoritative sources.")
    
    if not recommendations:
        recommendations.append("Content follows SEO best practices!")
    
    return recommendations


def _format_results(metrics: Dict, recommendations: List[str]) -> str:
    """Format SEO analysis results"""
    
    keyword_section = ""
    if 'target_keyword' in metrics:
        keyword_section = f"""
KEYWORD ANALYSIS:
- Target Keyword: {metrics['target_keyword']}
- Keyword Count: {metrics['keyword_count']}
- Keyword Density: {metrics['keyword_density']:.2f}%
- In Title: {'YES' if metrics['in_title'] else 'NO'}
- In First Paragraph: {'YES' if metrics['in_first_paragraph'] else 'NO'}
"""
    
    top_kw_str = ", ".join([f"{word} ({count})" for word, count in metrics['top_keywords']])
    
    result = f"""
SEO ANALYSIS RESULTS
====================

CONTENT METRICS:
- Word Count: {metrics['word_count']} words
- Sentences: {metrics['sentence_count']}
- Average Sentence Length: {metrics['avg_sentence_length']:.1f} words

READABILITY:
- Flesch Reading Ease: {metrics['flesch_reading_ease']:.1f}/100
- Grade Level: {metrics['grade_level']:.1f}
- Rating: {metrics['readability_rating']}
{keyword_section}
TOP KEYWORDS: {top_kw_str}

STRUCTURE:
- H1 Headers: {metrics['h1_count']} (should be 1)
- H2 Headers: {metrics['h2_count']} (aim for 3-5)
- Total Headers: {metrics['total_headers']}

SEO SCORE: {_calculate_seo_score(metrics)}/100

RECOMMENDATIONS:
"""
    
    for i, rec in enumerate(recommendations, 1):
        result += f"{i}. {rec}\n"
    
    return result


def _calculate_seo_score(metrics: Dict) -> int:
    """Calculate overall SEO score (0-100)"""
    score = 0
    
    if 800 <= metrics['word_count'] <= 2000:
        score += 20
    elif 500 <= metrics['word_count'] < 800:
        score += 15
    
    if 60 <= metrics['flesch_reading_ease'] <= 80:
        score += 20
    elif 50 <= metrics['flesch_reading_ease'] < 60:
        score += 15
    
    if metrics['has_proper_title'] and metrics['h1_count'] == 1:
        score += 10
    if metrics['has_subheaders']:
        score += 10
    
    if 'target_keyword' in metrics:
        if 0.5 <= metrics['keyword_density'] <= 2.5:
            score += 7
        if metrics['in_title']:
            score += 5
        if metrics['in_first_paragraph']:
            score += 4
    else:
        score += 15
    
    if metrics['internal_links'] > 0:
        score += 5
    if metrics['external_links'] > 0:
        score += 5
    
    if metrics['has_meta_description']:
        score += 10
    
    return min(score, 100)