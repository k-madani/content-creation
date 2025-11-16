import os
from crewai import Agent
from crewai_tools import SerperDevTool
from tools.tone_analyzer import ToneAnalyzerTool

# Initialize tools
search_tool = SerperDevTool()
tone_tool = ToneAnalyzerTool()

def create_research_agent():
    """Research agent that gathers information from web sources"""
    return Agent(
        role='Content Researcher',
        goal='Gather accurate, relevant, and up-to-date information on any given topic',
        backstory='''You are an experienced research journalist with expertise in 
                     finding credible sources and verifying information. You excel at 
                     distinguishing between reliable and unreliable sources. You always 
                     cross-reference facts and provide comprehensive research summaries.''',
        tools=[search_tool],
        verbose=True,
        allow_delegation=False
    )

def create_tone_analysis_agent():
    """Agent that analyzes and defines writing tone"""
    return Agent(
        role='Tone Analyst',
        goal='Analyze writing style and provide guidelines for consistent tone',
        backstory='''You are an expert in communication and writing style analysis. 
                     You understand how different tones affect reader perception and 
                     can provide clear guidelines for matching specific writing styles.''',
        tools=[tone_tool],
        verbose=True,
        allow_delegation=False
    )

def create_writer_agent():
    """Writer agent that creates engaging content"""
    return Agent(
        role='Content Writer',
        goal='Write clear, engaging, and informative content following provided tone guidelines',
        backstory='''You are a professional content writer with 10 years of experience 
                     creating blog posts and articles. You excel at adapting your writing 
                     style to match specific tones and audiences. You write in a clear, 
                     accessible style that engages readers while following tone guidelines precisely.''',
        verbose=True,
        allow_delegation=False
    )

def create_editor_agent():
    """Editor agent that polishes and improves content"""
    return Agent(
        role='Content Editor',
        goal='Review and improve content for clarity, grammar, flow, and engagement',
        backstory='''You are a meticulous editor with an exceptional eye for detail. 
                     You improve content by fixing grammar errors, enhancing clarity, 
                     ensuring logical flow, and making writing more engaging. You cut 
                     unnecessary words and expand where more explanation is needed. 
                     You ensure consistency in tone and style throughout.''',
        verbose=True,
        allow_delegation=False
    )

def create_seo_agent():
    """Agent that optimizes content for SEO"""
    from tools.seo_optimizer import SEOOptimizerTool
    
    seo_tool = SEOOptimizerTool()
    
    return Agent(
        role='SEO Specialist',
        goal='Optimize content for search engines while maintaining quality and readability',
        backstory='''You are an SEO expert who understands both technical optimization 
                     and user experience. You know how to improve search rankings without 
                     sacrificing content quality. You provide clear, actionable recommendations 
                     for content optimization.''',
        tools=[],  # SEO tool will be called manually in task
        verbose=True,
        allow_delegation=False
    )