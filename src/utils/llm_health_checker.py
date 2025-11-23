"""
LLM Health Checker
Tests LLM availability before execution and enables auto-fallback
"""

import os
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


class LLMHealthChecker:
    """Check which LLMs are available and healthy"""
    
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.health_status = {}
    
    def check_all_providers(self):
        """Health check all providers"""
        
        console.print("\n[cyan]🏥 Running LLM Health Checks...[/cyan]\n")
        
        # Check Gemini
        if self.gemini_key:
            gemini_healthy = self._test_gemini()
            self.health_status['gemini'] = gemini_healthy
        else:
            console.print("  [dim]⚠️ Gemini: No API key[/dim]")
            self.health_status['gemini'] = False
        
        # Check Groq
        if self.groq_key:
            groq_healthy = self._test_groq()
            self.health_status['groq'] = groq_healthy
        else:
            console.print("  [dim]⚠️ Groq: No API key[/dim]")
            self.health_status['groq'] = False
        
        # Summary
        healthy_providers = [k for k, v in self.health_status.items() if v]
        
        if not healthy_providers:
            console.print("\n[red]❌ No healthy LLM providers available![/red]")
            console.print("[yellow]Please check your API keys and try again.[/yellow]\n")
            return None
        
        console.print(f"\n[green]✅ {len(healthy_providers)} provider(s) available: {', '.join(healthy_providers)}[/green]\n")
        
        # Return best available
        if self.health_status.get('gemini'):
            return 'gemini/gemini-2.5-flash'
        elif self.health_status.get('groq'):
            return 'groq/llama-3.3-70b-versatile'
        
        return None
    
    def _test_gemini(self):
        """Test Gemini API"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Quick test
            response = model.generate_content("Say 'ok'")
            
            if response.text:
                console.print("  [green]✅ Gemini: Healthy[/green]")
                return True
            
        except Exception as e:
            error_msg = str(e)
            
            if "429" in error_msg or "quota" in error_msg.lower():
                console.print("  [yellow]⚠️ Gemini: Rate limited (quota exceeded)[/yellow]")
            elif "404" in error_msg:
                console.print("  [yellow]⚠️ Gemini: Model not found[/yellow]")
            elif "401" in error_msg or "403" in error_msg:
                console.print("  [red]❌ Gemini: Invalid API key[/red]")
            else:
                console.print(f"  [yellow]⚠️ Gemini: {str(e)[:50]}...[/yellow]")
            
            return False
        
        return False
    
    def _test_groq(self):
        """Test Groq API"""
        try:
            from groq import Groq
            
            client = Groq(api_key=self.groq_key)
            
            # Quick test
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say 'ok'"}],
                max_tokens=5
            )
            
            if response.choices[0].message.content:
                console.print("  [green]✅ Groq: Healthy[/green]")
                return True
            
        except Exception as e:
            error_msg = str(e)
            
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                console.print("  [yellow]⚠️ Groq: Rate limited[/yellow]")
            elif "401" in error_msg or "403" in error_msg:
                console.print("  [red]❌ Groq: Invalid API key[/red]")
            else:
                console.print(f"  [yellow]⚠️ Groq: {str(e)[:50]}...[/yellow]")
            
            return False
        
        return False
    
    def get_fallback_chain(self):
        """Get ordered list of healthy providers"""
        
        chain = []
        
        if self.health_status.get('gemini'):
            chain.append('gemini/gemini-2.5-flash')
        
        if self.health_status.get('groq'):
            chain.append('groq/llama-3.3-70b-versatile')
        
        return chain


# Singleton
health_checker = LLMHealthChecker()