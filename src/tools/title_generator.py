"""
Safe LLM-Powered Title Generator Tool
Uses AI to generate creative titles with multiple fallback levels
"""

from crewai.tools import tool
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Configuration flag - set to False to disable LLM usage
ENABLE_LLM_GENERATION = True


@tool("Title Generator")
def title_generator(topic: str, tone: str = "professional", count: int = 5) -> str:
    """
    Generates creative title variations using AI when available.
    Has multiple fallback levels to ensure it always returns useful titles.
    
    Args:
        topic: The content topic
        tone: Target tone (professional, casual, technical)
        count: Number of variations (default: 5)
        
    Returns:
        Formatted list of title options with scores
    """
    
    # Safety: Return simple title if LLM disabled
    if not ENABLE_LLM_GENERATION:
        return _simple_title_response(topic)
    
    try:
        # Try LLM generation
        llm = _get_llm()
        titles = _generate_with_llm(llm, topic, tone, count)
        
        # Score and format
        scored_titles = []
        for title_text in titles:
            score = _score_title(title_text, topic)
            scored_titles.append({'title': title_text, 'score': score})
        
        scored_titles.sort(key=lambda x: x['score'], reverse=True)
        
        return _format_results(scored_titles, topic)
        
    except Exception as e:
        # Fallback: Return simple template titles
        return _fallback_response(topic, tone, count)


def _get_llm():
    """Get available LLM with fallback chain"""
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    # Try Gemini first
    if gemini_key and gemini_key.startswith('AIza'):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=gemini_key,
                temperature=0.9
            )
        except:
            pass
    
    # Fallback to Groq
    if groq_key and groq_key.startswith('gsk_'):
        try:
            from langchain_groq import ChatGroq
            return ChatGroq(
                api_key=groq_key,
                model="llama-3.3-70b-versatile",
                temperature=0.9
            )
        except:
            pass
    
    # If both fail, raise to trigger fallback
    raise Exception("No LLM available")


def _generate_with_llm(llm, topic: str, tone: str, count: int) -> list:
    """Use LLM to generate creative titles"""
    
    prompt = f"""Generate {count} creative, engaging titles for content about: "{topic}"

Tone: {tone}

Requirements:
- Each title should be 50-70 characters long
- Make titles attention-grabbing and SEO-friendly
- Use varied styles: questions, how-to guides, listicles, ultimate guides, etc.
- Be creative and contextually appropriate for this specific topic
- Include numbers in some titles (e.g., "7 Ways...", "10 Tips...")
- Make each title unique and compelling
- Ensure titles accurately reflect the topic

Output ONLY the titles, one per line, numbered. No explanations.

Format:
1. [First title]
2. [Second title]
3. [Third title]
etc."""

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, 'content') else str(response)
    
    # Parse titles from response
    titles = []
    for line in content.split('\n'):
        line = line.strip()
        # Match "1. Title" or "1) Title" or "1 - Title"
        match = re.match(r'^\d+[\.\)\-\:]\s*(.+)$', line)
        if match:
            title = match.group(1).strip().strip('"\'')
            if title and len(title) > 10:
                titles.append(title)
    
    # Fallback parsing if above fails
    if not titles:
        parts = re.split(r'\d+[\.\)]\s*', content)
        titles = [t.strip().strip('"\'') for t in parts if len(t.strip()) > 10]
    
    # If still no titles, use fallback
    if not titles:
        titles = _create_template_titles(topic, tone, count)
    
    return titles[:count]


def _create_template_titles(topic: str, tone: str, count: int) -> list:
    """Create template-based titles as fallback"""
    
    titles = []
    topic_clean = topic.strip()
    
    # Basic templates that work for most topics
    titles.append(f"The Complete Guide to {topic_clean}")
    titles.append(f"Understanding {topic_clean}: Key Insights for 2025")
    titles.append(f"{topic_clean}: Everything You Need to Know")
    titles.append(f"Mastering {topic_clean}: Expert Tips and Strategies")
    titles.append(f"{topic_clean}: A Comprehensive Overview")
    titles.append(f"The Essential Guide to {topic_clean}")
    titles.append(f"Exploring {topic_clean}: In-Depth Analysis")
    
    return titles[:count]


def _fallback_response(topic: str, tone: str, count: int) -> str:
    """Generate fallback response when LLM fails"""
    
    # Use template titles
    titles = _create_template_titles(topic, tone, count)
    
    # Score them
    scored_titles = []
    for title_text in titles:
        score = _score_title(title_text, topic)
        scored_titles.append({'title': title_text, 'score': score})
    
    scored_titles.sort(key=lambda x: x['score'], reverse=True)
    
    result = f"""
TITLE SUGGESTIONS (Template Mode)
===================================
Topic: {topic}
Note: Using template-based titles (LLM unavailable)

RANKED TITLES:
"""
    
    for i, item in enumerate(scored_titles, 1):
        marker = " <- RECOMMENDED" if i == 1 else ""
        result += f"\n{i}. \"{item['title']}\"{marker}\n"
        result += f"   SEO Score: {item['score']}/100\n"
    
    result += f"\n{'='*60}\n"
    result += f"RECOMMENDATION: \"{scored_titles[0]['title']}\"\n"
    
    return result


def _simple_title_response(topic: str) -> str:
    """Simplest possible response"""
    return f"Suggested Title: {topic.strip()}"


def _score_title(title: str, topic: str) -> int:
    """Score a title for SEO and engagement (0-100)"""
    
    score = 0
    
    # 1. Length Score (25 points) - More lenient
    title_len = len(title)
    if 40 <= title_len <= 70:
        score += 25
    elif 30 <= title_len <= 80:
        score += 20
    else:
        score += 15
    
    # 2. Topic Inclusion (30 points) - More generous
    topic_words = [w for w in topic.lower().split() if len(w) > 2]
    if topic_words:
        topic_in_title = sum(1 for word in topic_words if word in title.lower())
        if topic_in_title >= len(topic_words) * 0.7:  # 70% coverage
            score += 30
        elif topic_in_title >= len(topic_words) * 0.5:  # 50% coverage
            score += 20
        else:
            score += 10
    else:
        score += 20
    
    # 3. Engagement Words (25 points) - Expanded list
    power_words = ['complete', 'essential', 'ultimate', 'best', 'guide', 'mastering',
                   'expert', 'comprehensive', 'key', 'advanced', 'simple', 'easy',
                   'proven', 'effective', 'practical', 'epic', 'must', 'perfect',
                   'amazing', 'incredible', 'secrets', 'tips', 'strategies', 'ways']
    power_count = sum(1 for pw in power_words if pw in title.lower())
    if power_count >= 2:
        score += 25
    elif power_count >= 1:
        score += 20
    else:
        score += 10
    
    # 4. Numbers (15 points)
    has_number = any(char.isdigit() for char in title)
    score += 15 if has_number else 5
    
    # 5. Clarity Bonus (5 points)
    # No overly complex jargon
    complex = ['paradigm', 'synergy', 'leverage', 'utilize', 'holistic']
    has_jargon = any(cw in title.lower() for cw in complex)
    score += 5 if not has_jargon else 2
    
    return min(score, 100)


def _format_results(scored_titles: list, topic: str) -> str:
    """Format title generation results"""
    
    result = f"""
TITLE SUGGESTIONS
==================
Topic: {topic}
Generated: {len(scored_titles)} AI-powered options

RANKED TITLES:
"""
    
    for i, item in enumerate(scored_titles, 1):
        marker = " <- RECOMMENDED" if i == 1 else ""
        result += f"\n{i}. \"{item['title']}\"{marker}\n"
        result += f"   SEO Score: {item['score']}/100\n"
    
    result += f"\n{'='*60}\n"
    result += f"RECOMMENDATION: Use Title #1\n"
    result += f"\"{scored_titles[0]['title']}\"\n"
    result += f"Score: {scored_titles[0]['score']}/100\n"
    
    return result


def generate_titles(topic: str, tone: str = "professional", count: int = 5) -> str:
    """
    Core function to generate title variations (for direct imports)
    Same as the tool version but can be imported directly
    """
    return title_generator._run(topic=topic, tone=tone, count=count)


def get_best_title(topic: str, tone: str = "professional") -> str:
    """Quick function to get just the best title"""
    try:
        llm = _get_llm()
        titles = _generate_with_llm(llm, topic, tone, 5)
        scored = [(t, _score_title(t, topic)) for t in titles]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0]
    except:
        return f"The Complete Guide to {topic.strip()}"