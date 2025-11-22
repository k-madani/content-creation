"""
Content Creation Agents with Free LLM Support
Uses LiteLLM format for model names
"""

from crewai import Agent
import os
from dotenv import load_dotenv

load_dotenv()

class ContentAgents:
    """Factory class for creating content creation agents"""
    
    def __init__(self):
        """Initialize LLM configurations"""
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.llm_strategy = os.getenv("LLM_STRATEGY", "gemini_first")
        
        # Set API keys in environment for LiteLLM
        if self.gemini_key:
            os.environ["GEMINI_API_KEY"] = self.gemini_key
        if self.groq_key:
            os.environ["GROQ_API_KEY"] = self.groq_key
        
        # Initialize primary LLM (string format for LiteLLM)
        self.llm = self._get_primary_llm()
        self.fallback_llm = self._get_fallback_llm()
    
    def _get_primary_llm(self):
        """Get primary LLM in LiteLLM format"""
        if self.llm_strategy == "groq_first" and self.groq_key:
            print("🟠 Using Groq as primary LLM")
            return "groq/llama-3.3-70b-versatile"
        elif self.gemini_key:
            print("🔵 Using Gemini as primary LLM")
            return "gemini/gemini-1.5-flash"
        elif self.groq_key:
            print("🟠 Using Groq as primary LLM (Gemini not available)")
            return "groq/llama-3.3-70b-versatile"
        else:
            raise Exception(
                "No LLM provider available. Please add GEMINI_API_KEY or GROQ_API_KEY to .env file"
            )
    
    def _get_fallback_llm(self):
        """Get fallback LLM"""
        if self.groq_key:
            return "groq/llama-3.3-70b-versatile"
        else:
            return self.llm
    
    def research_agent(self, tools: list) -> Agent:
        """Research Agent - Gathers information and insights"""
        return Agent(
            role="Content Research Specialist",
            goal="Conduct comprehensive research on given topics using available tools. Gather accurate, up-to-date information from multiple sources.",
            backstory="You are an expert research analyst with years of experience in content research. You have a keen eye for finding reliable sources and synthesizing complex topics into clear insights.",
            tools=tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=5
        )
    
    def writer_agent(self, tools: list) -> Agent:
        """Writer Agent - Creates engaging content"""
        return Agent(
            role="Content Writer",
            goal="Create high-quality, engaging content that resonates with the target audience.",
            backstory="You are a professional content writer with extensive experience across multiple formats. You understand audience psychology and storytelling principles.",
            tools=tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=5
        )
    
    def editor_agent(self, tools: list) -> Agent:
        """Editor Agent - Refines and polishes content"""
        return Agent(
            role="Content Editor",
            goal="Review, refine, and polish content to ensure highest quality.",
            backstory="You are an experienced content editor with a sharp eye for detail. You excel at improving structure and maintaining consistent tone.",
            tools=tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=5
        )
    
    def seo_agent(self, tools: list) -> Agent:
        """SEO Agent - Optimizes content for search engines"""
        return Agent(
            role="SEO Specialist",
            goal="Optimize content for search engines while maintaining readability and user value.",
            backstory="You are an SEO expert with deep knowledge of search engine algorithms. You excel at keyword research and on-page optimization.",
            tools=tools,
            llm=self.llm,
            verbose=True,
            allow_delegation=False,
            max_iter=5
        )
    
    def controller_agent(self) -> Agent:
        """Controller Agent - Orchestrates the content creation workflow"""
        return Agent(
            role="Content Project Manager",
            goal="Orchestrate the entire content creation process by coordinating research, writing, editing, and SEO optimization.",
            backstory="You are an experienced project manager specializing in content creation workflows. You excel at delegating work effectively and ensuring quality.",
            llm=self.llm,
            verbose=True,
            allow_delegation=True,
            max_iter=10
        )

# Create global instance
content_agents = ContentAgents()