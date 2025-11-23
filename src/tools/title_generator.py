"""
Title Generator Tool
Generates multiple title variations using different strategies
"""

from crewai.tools import tool
import re
from typing import List, Dict


def generate_titles(topic: str, tone: str = "professional", count: int = 5) -> str:
    """
    Core function to generate title variations
    
    Args:
        topic: The content topic
        tone: Target tone (professional, casual, technical, etc.)
        count: Number of title variations to generate
        
    Returns:
        Formatted list of title options with scores
    """
    # Generate titles using different strategies
    titles = _generate_title_variations(topic, tone, count)
    
    # Score each title
    scored_titles = []
    for title_text, strategy in titles:
        score = _score_title(title_text, topic, tone)
        scored_titles.append({
            'title': title_text,
            'strategy': strategy,
            'score': score['total'],
            'breakdown': score['breakdown']
        })
    
    # Sort by score
    scored_titles.sort(key=lambda x: x['score'], reverse=True)
    
    # Format output
    return _format_title_results(scored_titles, topic)


@tool("Title Generator")
def title_generator(topic: str, tone: str = "professional", count: int = 5) -> str:
    """
    Tool version: Generates multiple title variations for content.
    Uses 5 different title strategies to create engaging, SEO-friendly options.
    
    Args:
        topic: The content topic
        tone: Target tone (professional, casual, technical)
        count: Number of variations (default: 5)
        
    Returns:
        Formatted list of title options with scores
    """
    return generate_titles(topic, tone, count)


def _generate_title_variations(topic: str, tone: str, count: int) -> List[tuple]:
    """Generate title variations using different strategies"""
    
    titles = []
    topic_clean = topic.strip()
    
    # Strategy 1: Question-Based
    if tone.lower() in ['casual', 'conversational']:
        titles.append((f"How Does {topic_clean} Actually Work?", "question"))
    else:
        titles.append((f"How {topic_clean} Transforms Modern Practices", "question"))
    
    # Strategy 2: Number-Based (Listicle)
    numbers = [7, 10, 5]
    if tone.lower() == 'casual':
        titles.append((f"{numbers[0]} Amazing Things About {topic_clean} You Should Know", "number"))
    else:
        titles.append((f"{numbers[0]} Key Insights Into {topic_clean}", "number"))
    
    # Strategy 3: Ultimate Guide
    if tone.lower() in ['professional', 'technical']:
        titles.append((f"The Comprehensive Guide to {topic_clean}", "guide"))
    else:
        titles.append((f"Everything You Need to Know About {topic_clean}", "guide"))
    
    # Strategy 4: Year/Timeliness
    titles.append((f"{topic_clean}: Essential Insights for 2025", "timely"))
    
    # Strategy 5: Benefit/Outcome Focused
    if tone.lower() == 'casual':
        titles.append((f"Why {topic_clean} Matters More Than You Think", "outcome"))
    else:
        titles.append((f"Understanding {topic_clean}: Benefits and Applications", "outcome"))
    
    # Strategy 6: Best/Top Format
    titles.append((f"The Best Approaches to {topic_clean}", "superlative"))
    
    # Return requested count
    return titles[:count]


def _score_title(title: str, topic: str, tone: str) -> Dict:
    """Score a title across multiple dimensions"""
    
    score_breakdown = {}
    
    # 1. Length Score (30 points)
    title_len = len(title)
    if 50 <= title_len <= 60:
        score_breakdown['length'] = 30
    elif 40 <= title_len <= 70:
        score_breakdown['length'] = 20
    else:
        score_breakdown['length'] = 10
    
    # 2. Topic Inclusion (25 points)
    topic_words = topic.lower().split()
    topic_in_title = sum(1 for word in topic_words if word in title.lower())
    topic_coverage = (topic_in_title / len(topic_words)) * 25 if topic_words else 0
    score_breakdown['topic_match'] = int(topic_coverage)
    
    # 3. Power Words (20 points)
    power_words = {
        'professional': ['comprehensive', 'essential', 'guide', 'complete', 'key', 'insights'],
        'casual': ['amazing', 'awesome', 'should', 'need', 'actually', 'really'],
        'technical': ['advanced', 'deep', 'analysis', 'understanding', 'approaches']
    }
    
    relevant_power_words = power_words.get(tone.lower(), power_words['professional'])
    has_power_word = any(pw in title.lower() for pw in relevant_power_words)
    score_breakdown['power_words'] = 20 if has_power_word else 5
    
    # 4. Numbers (15 points)
    has_number = any(char.isdigit() for char in title)
    score_breakdown['numbers'] = 15 if has_number else 0
    
    # 5. Clarity (10 points)
    complex_words = ['paradigm', 'leverage', 'utilize', 'synergy', 'holistic']
    has_jargon = any(cw in title.lower() for cw in complex_words)
    score_breakdown['clarity'] = 5 if has_jargon else 10
    
    # Calculate total
    total = sum(score_breakdown.values())
    
    return {
        'total': min(total, 100),
        'breakdown': score_breakdown
    }


def _format_title_results(scored_titles: List[Dict], topic: str) -> str:
    """Format title generation results"""
    
    result = f"""
TITLE GENERATION RESULTS
========================
Topic: {topic}
Generated: {len(scored_titles)} variations

RANKED TITLE OPTIONS:
"""
    
    for i, item in enumerate(scored_titles, 1):
        marker = "⭐ RECOMMENDED" if i == 1 else ""
        result += f"\n{i}. \"{item['title']}\" {marker}\n"
        result += f"   Strategy: {item['strategy']}\n"
        result += f"   Score: {item['score']}/100\n"
        
        # Show breakdown
        b = item['breakdown']
        result += f"   Breakdown: Length({b['length']}) "
        result += f"Topic({b['topic_match']}) "
        result += f"Power({b['power_words']}) "
        result += f"Numbers({b['numbers']}) "
        result += f"Clarity({b['clarity']})\n"
    
    result += f"\n{'='*60}\n"
    result += f"💡 RECOMMENDATION: Use Title #1 (Score: {scored_titles[0]['score']}/100)\n"
    result += f"   \"{scored_titles[0]['title']}\"\n"
    
    return result


# For backward compatibility and direct calling
def get_best_title(topic: str, tone: str = "professional") -> str:
    """Quick function to get just the best title"""
    titles = _generate_title_variations(topic, tone, 5)
    scored_titles = []
    
    for title_text, strategy in titles:
        score = _score_title(title_text, topic, tone)
        scored_titles.append({
            'title': title_text,
            'score': score['total']
        })
    
    scored_titles.sort(key=lambda x: x['score'], reverse=True)
    return scored_titles[0]['title']