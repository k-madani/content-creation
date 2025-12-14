"""
Free Research Tool - Complete with Error Handling
Wikipedia + DuckDuckGo with fallback strategies
"""

from crewai.tools import tool
import wikipedia
from ddgs import DDGS
import time


@tool("Free Research Tool")
def research_tool(query: str, max_results: int = 5) -> str:
    """
    Searches Wikipedia and DuckDuckGo with comprehensive error handling
    """
    results = []
    errors = []
    
    # Try Wikipedia
    try:
        wiki_results = _search_wikipedia(query)
        if wiki_results:
            results.append(wiki_results)
    except Exception as e:
        errors.append(('Wikipedia', str(e)[:50]))
    
    # Try DuckDuckGo with retry
    try:
        ddg_results = _search_duckduckgo_with_retry(query, max_results)
        if ddg_results:
            results.extend(ddg_results)
    except Exception as e:
        errors.append(('DuckDuckGo', str(e)[:50]))
    
    # FALLBACK: Try simplified query if no results
    if not results and len(query.split()) > 3:
        simplified = ' '.join(query.split()[:3])
        try:
            ddg_results = _search_duckduckgo_with_retry(simplified, max_results)
            if ddg_results:
                results.extend(ddg_results)
        except:
            pass
    
    # FINAL FALLBACK: Partial information
    if not results:
        error_list = '\n'.join([f'- {src}: {err}' for src, err in errors])
        return (
            f"# Research Results for: {query}\n\n"
            f"⚠️ **Limited results found**\n\n"
            f"Search attempts:\n"
            f"{error_list}\n\n"
            f"💡 Content can still be generated using general knowledge.\n"
        )
    
    # Format results
    formatted = f"# Research Results for: {query}\n\n"
    formatted += f"✅ Found {len(results)} source(s)\n\n"
    
    for i, result in enumerate(results[:max_results], 1):
        formatted += f"## Result {i}: {result['title']}\n"
        formatted += f"**Source:** {result['source']}\n"
        formatted += f"**Summary:** {result['content']}\n"
        if 'url' in result:
            formatted += f"**URL:** {result['url']}\n"
        formatted += "\n---\n\n"
    
    return formatted


def _search_wikipedia(query: str):
    """Search Wikipedia with error handling"""
    try:
        summary = wikipedia.summary(query, sentences=5, auto_suggest=True)
        page = wikipedia.page(query, auto_suggest=True)
        return {
            "title": page.title,
            "source": "Wikipedia",
            "content": summary,
            "url": page.url
        }
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            page = wikipedia.page(e.options[0])
            return {
                "title": page.title,
                "source": "Wikipedia",
                "content": wikipedia.summary(e.options[0], sentences=5),
                "url": page.url
            }
        except:
            return None
    except:
        return None


def _search_duckduckgo_with_retry(query: str, max_results: int):
    """Search DuckDuckGo with retry logic"""
    
    for attempt in range(3):
        try:
            ddgs = DDGS()
            search_results = list(ddgs.text(query, max_results=max_results))
            
            formatted_results = []
            for result in search_results:
                formatted_results.append({
                    "title": result.get('title', 'No Title'),
                    "source": "DuckDuckGo",
                    "content": result.get('body', 'No summary'),
                    "url": result.get('href', '')
                })
            
            return formatted_results
            
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
                continue
            return []
    
    return []