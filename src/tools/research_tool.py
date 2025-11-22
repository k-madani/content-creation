"""
Free Research Tool - Replaces Serper
Uses Wikipedia + DuckDuckGo Search
Updated for CrewAI 1.5.0+
"""

from crewai.tools import tool
import wikipedia
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup


@tool("Free Research Tool")
def research_tool(query: str, max_results: int = 5) -> str:
    """
    Searches Wikipedia and DuckDuckGo for comprehensive research.
    Use this for gathering information, facts, and recent developments on any topic.
    Returns structured summaries from multiple sources.
    
    Args:
        query: Search query for research
        max_results: Maximum number of results (default: 5)
        
    Returns:
        Formatted research results from multiple sources
    """
    results = []
    
    # 1. Search Wikipedia
    try:
        wiki_results = _search_wikipedia(query)
        if wiki_results:
            results.append(wiki_results)
    except Exception as e:
        print(f"Wikipedia search failed: {e}")
    
    # 2. Search DuckDuckGo
    try:
        ddg_results = _search_duckduckgo(query, max_results)
        if ddg_results:
            results.extend(ddg_results)
    except Exception as e:
        print(f"DuckDuckGo search failed: {e}")
    
    # Format results
    if not results:
        return f"No results found for query: {query}"
    
    formatted = f"# Research Results for: {query}\n\n"
    for i, result in enumerate(results[:max_results], 1):
        formatted += f"## Result {i}: {result['title']}\n"
        formatted += f"**Source:** {result['source']}\n"
        formatted += f"**Summary:** {result['content']}\n"
        if 'url' in result:
            formatted += f"**URL:** {result['url']}\n"
        formatted += "\n---\n\n"
    
    return formatted


def _search_wikipedia(query: str):
    """Search Wikipedia for information"""
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


def _search_duckduckgo(query: str, max_results: int):
    """Search DuckDuckGo for web results"""
    try:
        ddgs = DDGS()
        search_results = list(ddgs.text(query, max_results=max_results))
        
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "title": result.get('title', 'No Title'),
                "source": "DuckDuckGo",
                "content": result.get('body', 'No summary available'),
                "url": result.get('href', '')
            })
        
        return formatted_results
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return []