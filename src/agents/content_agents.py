"""
Content Creation Agents - Complete Implementation
With: Prompt templates, health check, fallback, load balancing
FIXED: Proper provider prefixes and load distribution
"""

from crewai import Agent
import os
from dotenv import load_dotenv
from rich.console import Console
import litellm
from prompts.prompt_templates import PromptTemplates, sanitize_user_input

load_dotenv()
console = Console()

# Configure LiteLLM globally
litellm.drop_params = True
litellm.set_verbose = False


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
            self.fallback_chain.append(('gemini/gemini-2.0-flash-exp', 'Gemini'))
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
            console.print(f"\n[cyan]Fallback Chain ({len(self.fallback_chain)} providers):[/cyan]")
            for i, (model, name) in enumerate(self.fallback_chain, 1):
                prefix = "[Primary]" if i == 1 else "[Fallback]"
                console.print(f"  {i}. {prefix} {name}")
        
        if healthy > 0:
            primary_model, primary_name = self.fallback_chain[0]
            console.print(f"\n[bold green]Selected: {primary_name}[/bold green]\n")
        
        return healthy > 0
    
    def get_primary_llm(self, strategy="gemini_first"):
        """Get best available LLM"""
        
        if strategy == "groq_first":
            for model, name in self.fallback_chain:
                if 'groq' in model:
                    return model
        
        if self.fallback_chain:
            model, name = self.fallback_chain[0]
            return model
        
        return None


class ContentAgents:
    """Factory for content creation agents with prompt templates and load balancing"""
    
    def __init__(self):
        """Initialize with health check"""
        
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.llm_strategy = os.getenv("LLM_STRATEGY", "gemini_first")
        
        # Initialize prompt templates
        self.templates = PromptTemplates()
        
        # Set environment variables for LiteLLM
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
        
        # LOAD BALANCED: Distribute work across both providers
        # Research is heavy (162s) → Use Gemini (higher daily limit: 1500/day)
        # Writer needs quality → Use Gemini  
        # Editor is fast (<1s) → Use Groq (faster inference: 30/min)
        # SEO is fast (<1s) → Use Groq
        
        if self.health_checker.health_status.get('gemini'):
            self.research_llm = 'gemini/gemini-2.0-flash-exp'
            self.writer_llm = 'gemini/gemini-2.0-flash-exp'
        else:
            # Fallback to Groq if Gemini unavailable
            self.research_llm = 'groq/llama-3.3-70b-versatile'
            self.writer_llm = 'groq/llama-3.3-70b-versatile'
        
        if self.health_checker.health_status.get('groq'):
            self.editor_llm = 'groq/llama-3.3-70b-versatile'
            self.seo_llm = 'groq/llama-3.3-70b-versatile'
        else:
            # Fallback to Gemini if Groq unavailable
            self.editor_llm = 'gemini/gemini-2.0-flash-exp'
            self.seo_llm = 'gemini/gemini-2.0-flash-exp'
        
        self.fallback_chain = self.health_checker.fallback_chain
        self.has_fallback = len(self.fallback_chain) > 1
        
        # Display load balancing strategy
        self._display_load_balancing()
    
    def _display_load_balancing(self):
        """Display which provider handles which agent"""
        console.print(f"\n[cyan]Load Balanced Strategy:[/cyan]")
        
        # Research
        research_provider = "Gemini" if "gemini" in self.research_llm else "Groq"
        console.print(f"  Research → {research_provider} (heavy lifting, 162s)")
        
        # Writer
        writer_provider = "Gemini" if "gemini" in self.writer_llm else "Groq"
        console.print(f"  Writer → {writer_provider} (creative quality)")
        
        # Editor
        editor_provider = "Groq" if "groq" in self.editor_llm else "Gemini"
        console.print(f"  Editor → {editor_provider} (fast refinement, <1s)")
        
        # SEO
        seo_provider = "Groq" if "groq" in self.seo_llm else "Gemini"
        console.print(f"  SEO → {seo_provider} (final polish, <1s)")
        
        console.print()
    
    def research_agent(self, tools: list) -> Agent:
        """Research Agent with structured prompting"""
        
        return Agent(
            role=self.templates.RESEARCH_AGENT_PROMPT['role'],
            goal=self.templates.RESEARCH_AGENT_PROMPT['goal'],
            backstory=self.templates.RESEARCH_AGENT_PROMPT['backstory'],
            tools=tools,
            llm=self.research_llm,
            verbose=False,
            allow_delegation=False,
            max_iter=5
        )
    
    def writer_agent(self, tools: list) -> Agent:
        """Writer Agent with few-shot examples"""
        
        # Enhanced goal with few-shot examples
        enhanced_goal = (
            self.templates.WRITER_AGENT_PROMPT['goal'] + 
            "\n\n" + 
            "EXAMPLE OF GOOD INTRODUCTION:\n" +
            self.templates.WRITING_EXAMPLES['good_intro'] +
            "\n\n" +
            "EXAMPLE OF GOOD CONCLUSION:\n" +
            self.templates.WRITING_EXAMPLES['good_conclusion']
        )
        
        return Agent(
            role=self.templates.WRITER_AGENT_PROMPT['role'],
            goal=enhanced_goal,
            backstory=self.templates.WRITER_AGENT_PROMPT['backstory'],
            tools=tools,
            llm=self.writer_llm,
            verbose=False,
            allow_delegation=False,
            max_iter=5
        )
    
    def editor_agent(self, tools: list) -> Agent:
        """Editor Agent with structured prompting"""
        
        return Agent(
            role=self.templates.EDITOR_AGENT_PROMPT['role'],
            goal=self.templates.EDITOR_AGENT_PROMPT['goal'],
            backstory=self.templates.EDITOR_AGENT_PROMPT['backstory'],
            tools=tools,
            llm=self.editor_llm,
            verbose=False,
            allow_delegation=False,
            max_iter=5
        )
    
    def seo_agent(self, tools: list) -> Agent:
        """SEO Agent with structured prompting"""
        
        # Enhanced goal with SEO best practices
        enhanced_goal = (
            self.templates.SEO_AGENT_PROMPT['goal'] +
            "\n\n" +
            "SEO BEST PRACTICES:\n" +
            self.templates.SEO_GUIDELINES
        )
        
        return Agent(
            role=self.templates.SEO_AGENT_PROMPT['role'],
            goal=enhanced_goal,
            backstory=self.templates.SEO_AGENT_PROMPT['backstory'],
            tools=tools,
            llm=self.seo_llm,
            verbose=False,
            allow_delegation=False,
            max_iter=5
        )
    
    def controller_agent(self) -> Agent:
        """Enhanced Controller with decision-making prompts"""
        primary_llm = self.health_checker.get_primary_llm(self.llm_strategy)
        
        return Agent(
            role=self.templates.CONTROLLER_AGENT_PROMPT['role'],
            goal=self.templates.CONTROLLER_AGENT_PROMPT['goal'],
            backstory=self.templates.CONTROLLER_AGENT_PROMPT['backstory'],
            llm=primary_llm,
            verbose=False,
            allow_delegation=True,
            max_iter=15
        )


# Global instance
content_agents = ContentAgents()