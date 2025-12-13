"""
Content Creation Agents - Complete Implementation
With: Health check, fallback, load balancing across providers
"""

from crewai import Agent
import os
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


class LLMHealthChecker:
    """Check LLM availability and manage fallback"""
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.health_status = {}
        self.fallback_chain = []
    
    def check_all_providers(self):
        """Health check all providers"""
        
        console.print("\n[cyan]LLM Health Check...[/cyan]")
        
        if self.gemini_key and self.gemini_key.startswith('AIza'):
            console.print("  [green]OK Gemini: Available[/green]")
            self.health_status['gemini'] = True
            self.fallback_chain.append(('gemini/gemini-1.5-flash', 'Gemini 1.5'))
        else:
            console.print("  [dim]WARNING Gemini: Not configured[/dim]")
            self.health_status['gemini'] = False
        
        if self.groq_key and self.groq_key.startswith('gsk_'):
            console.print("  [green]OK Groq: Available[/green]")
            self.health_status['groq'] = True
            self.fallback_chain.append(('groq/llama-3.3-70b-versatile', 'Groq'))
        else:
            console.print("  [dim]WARNING Groq: Not configured[/dim]")
            self.health_status['groq'] = False
        
        healthy = sum(self.health_status.values())
        
        if self.fallback_chain:
            console.print(f"\n[cyan]Load Balanced Strategy:[/cyan]")
            console.print("  Research → Groq (heavy lifting)")
            console.print("  Writer → Gemini 1.5 (creative quality)")
            console.print("  Editor → Groq (fast refinement)")
            console.print("  SEO → Gemini 1.5 (final polish)")
        
        console.print()
        return healthy > 0
    
    def get_primary_llm(self, strategy="gemini_first"):
        """Get best available LLM"""
        
        if strategy == "groq_first":
            for model, name in self.fallback_chain:
                if 'groq' in model:
                    console.print(f"[cyan]Primary: {name}[/cyan]\n")
                    return model
        
        if self.fallback_chain:
            model, name = self.fallback_chain[0]
            console.print(f"[cyan]Primary: {name}[/cyan]\n")
            return model
        
        return None


class ContentAgents:
    """Factory for content creation agents with load balancing"""
    
    def __init__(self):
        """Initialize with health check"""
        
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.llm_strategy = os.getenv("LLM_STRATEGY", "balanced")
        
        if self.gemini_key:
            os.environ["GEMINI_API_KEY"] = self.gemini_key
        if self.groq_key:
            os.environ["GROQ_API_KEY"] = self.groq_key
        
        # Health check
        self.health_checker = LLMHealthChecker()
        
        if not self.health_checker.check_all_providers():
            raise Exception(
                "\nERROR: NO LLM PROVIDERS AVAILABLE!\n"
                "Add to .env:\n"
                "  GEMINI_API_KEY=... (https://aistudio.google.com/apikey)\n"
                "  GROQ_API_KEY=... (https://console.groq.com/keys)\n"
            )
        
        # Load balanced LLM assignment
        self.research_llm = 'groq/llama-3.3-70b-versatile'
        self.writer_llm = 'gemini/gemini-1.5-flash'
        self.editor_llm = 'groq/llama-3.3-70b-versatile'
        self.seo_llm = 'gemini/gemini-1.5-flash'
        
        self.fallback_chain = self.health_checker.fallback_chain
        self.has_fallback = len(self.fallback_chain) > 1
    
    def research_agent(self, tools: list) -> Agent:
        """Research Agent - Uses GROQ (handles multiple tool calls)"""
        return Agent(
            role="Content Research Specialist",
            goal=(
                "Gather comprehensive research using available tools. "
                "If initial searches fail, try alternative queries. "
                "Always provide useful findings even with limited results."
            ),
            backstory=(
                "You are a persistent research analyst. When searches fail, "
                "you adapt your approach and try different strategies. "
                "You never give up and always find valuable information."
            ),
            tools=tools,
            llm=self.research_llm,  # GROQ
            verbose=False,  # Reduced logging
            allow_delegation=False,
            max_iter=5
        )
    
    def writer_agent(self, tools: list) -> Agent:
        """Writer Agent - Uses GEMINI 1.5 (creative writing)"""
        return Agent(
            role="Content Writer",
            goal=(
                "Create high-quality content based on research. "
                "Use tone analyzer to match target tone. "
                "Always write - never refuse due to limited research."
            ),
            backstory=(
                "You are a professional writer who creates compelling content. "
                "Even with limited research, you produce valuable articles. "
                "You adapt your writing to available information."
            ),
            tools=tools,
            llm=self.writer_llm,  # GEMINI 1.5
            verbose=False,  # Reduced logging
            allow_delegation=False,
            max_iter=5
        )
    
    def editor_agent(self, tools: list) -> Agent:
        """Editor Agent - Uses GROQ (fast refinement)"""
        return Agent(
            role="Content Editor",
            goal=(
                "Refine content to highest quality. "
                "Improve readability, flow, and consistency. "
                "Always improve - never refuse to edit."
            ),
            backstory=(
                "You are an expert editor who enhances any content. "
                "You improve clarity, structure, and engagement."
            ),
            tools=tools,
            llm=self.editor_llm,  # GROQ
            verbose=False,  # Reduced logging
            allow_delegation=False,
            max_iter=5
        )
    
    def seo_agent(self, tools: list) -> Agent:
        """SEO Agent - Uses GEMINI 1.5 (final quality)"""
        return Agent(
            role="SEO Specialist",
            goal=(
                "Optimize content for search engines. "
                "Ensure proper keywords and meta tags. "
                "Always optimize what you receive."
            ),
            backstory=(
                "You are an SEO expert who maximizes content visibility. "
                "You optimize any content for better search rankings."
            ),
            tools=tools,
            llm=self.seo_llm,  # GEMINI 1.5
            verbose=False,  # Reduced logging
            allow_delegation=False,
            max_iter=5
        )
    
    def controller_agent(self) -> Agent:
        """Enhanced Controller - Uses primary LLM"""
        primary_llm = self.health_checker.get_primary_llm(self.llm_strategy)
        
        return Agent(
            role="Intelligent Content Project Manager",
            goal=(
                "Orchestrate content creation with adaptive decision-making. "
                "Monitor quality and adjust workflow as needed. "
                "Handle errors by finding alternative approaches. "
                "Make intelligent decisions about resource allocation. "
                "Learn from failures and optimize future generations."
            ),
            backstory=(
                "You are an AI-powered project manager with advanced reasoning. "
                "You analyze situations and adapt strategies dynamically. "
                "When quality is low, you identify root causes and adjust. "
                "When agents struggle, you find alternative approaches. "
                "You have decision-making authority to modify workflows, "
                "request additional research, or optimize parameters. "
                "Your goal is optimal outcomes, not just task completion."
            ),
            llm=primary_llm,
            verbose=False,  # Reduced logging
            allow_delegation=True,
            max_iter=15
        )


# Global instance
content_agents = ContentAgents()