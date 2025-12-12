"""
LLM Manager with Automatic Fallback
Handles Gemini → Groq fallback on rate limits
"""

import time
from typing import Optional, Dict, Any
from rich.console import Console
from collections import deque
from datetime import datetime

console = Console()


class LLMManager:
    """
    Centralized LLM management with automatic fallback
    
    Features:
    - Automatic Gemini → Groq fallback on rate limits
    - Exponential backoff retry strategy
    - Health monitoring and statistics
    - Transparent to agents
    """
    
    def __init__(self):
        # Provider configuration
        self.providers = [
            {
                'name': 'Gemini',
                'model': 'gemini/gemini-2.5-flash',
                'type': 'primary',
                'max_retries': 2,
                'rate_limit': 12  # Conservative (actual: 15/min)
            },
            {
                'name': 'Groq',
                'model': 'groq/llama-3.3-70b-versatile',
                'type': 'fallback',
                'max_retries': 3,
                'rate_limit': 25  # Conservative (actual: 30/min)
            }
        ]
        
        # Current provider index
        self.current_provider_idx = 0
        
        # Statistics tracking
        self.stats = {
            'Gemini': {'calls': 0, 'successes': 0, 'failures': 0, 'rate_limits': 0},
            'Groq': {'calls': 0, 'successes': 0, 'failures': 0, 'rate_limits': 0}
        }
        
        # Rate limiting tracking (sliding window)
        self.call_history = {
            'Gemini': deque(maxlen=15),
            'Groq': deque(maxlen=30)
        }
    
    def get_llm_string(self, prefer_groq: bool = False) -> str:
        """
        Get current LLM string for CrewAI agents
        
        Args:
            prefer_groq: Force Groq selection (useful for iteration-heavy tasks)
            
        Returns:
            LLM model string (e.g., 'gemini/gemini-2.5-flash')
        """
        
        if prefer_groq:
            provider = self.providers[1]  # Groq
            console.print(f"[dim]→ Using {provider['name']} (preferred for this task)[/dim]")
        else:
            provider = self.providers[self.current_provider_idx]
            
        return provider['model']
    
    def handle_failure(self, provider_name: str, error: Exception) -> Optional[str]:
        """
        Handle LLM failure and determine fallback strategy
        
        Args:
            provider_name: Name of provider that failed
            error: Exception that occurred
            
        Returns:
            Fallback LLM string if available, None if no fallback
        """
        
        # Update statistics
        self.stats[provider_name]['failures'] += 1
        
        # Check if it's a rate limit error
        is_rate_limit = self._is_rate_limit_error(error)
        
        if is_rate_limit:
            self.stats[provider_name]['rate_limits'] += 1
            console.print(f"[yellow]⚠️ {provider_name} rate limit detected[/yellow]")
        
        # Determine fallback
        if self.current_provider_idx < len(self.providers) - 1:
            # Switch to next provider
            self.current_provider_idx += 1
            fallback_provider = self.providers[self.current_provider_idx]
            
            console.print(f"[cyan]→ Switching to {fallback_provider['name']}[/cyan]")
            return fallback_provider['model']
        else:
            # No more fallbacks available
            console.print(f"[red]✗ All LLM providers exhausted[/red]")
            return None
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a rate limit error"""
        error_str = str(error).lower()
        return (
            '429' in error_str or
            'rate limit' in error_str or
            'ratelimit' in error_str or
            'too many requests' in error_str
        )
    
    def record_success(self, provider_name: str):
        """Record successful LLM call"""
        self.stats[provider_name]['calls'] += 1
        self.stats[provider_name]['successes'] += 1
        self.call_history[provider_name].append(datetime.now())
    
    def should_use_rate_limiting(self, provider_name: str) -> bool:
        """
        Check if we should proactively wait to avoid rate limits
        
        Returns:
            True if we should wait before next call
        """
        
        provider = next(p for p in self.providers if p['name'] == provider_name)
        history = self.call_history[provider_name]
        
        if len(history) < provider['rate_limit']:
            return False
        
        # Check if we've made too many calls in last 60 seconds
        now = datetime.now()
        recent_calls = sum(1 for call_time in history 
                          if (now - call_time).total_seconds() < 60)
        
        return recent_calls >= provider['rate_limit']
    
    def wait_if_needed(self, provider_name: str):
        """Proactively wait if approaching rate limit"""
        
        if self.should_use_rate_limiting(provider_name):
            history = self.call_history[provider_name]
            oldest_call = min(history)
            wait_time = 60 - (datetime.now() - oldest_call).total_seconds()
            
            if wait_time > 0:
                console.print(f"[yellow]⏳ Rate limit prevention: waiting {wait_time:.1f}s...[/yellow]")
                time.sleep(wait_time + 1)
    
    def reset_to_primary(self):
        """Reset to primary provider (call between attempts)"""
        self.current_provider_idx = 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            'current_provider': self.providers[self.current_provider_idx]['name'],
            'stats': self.stats,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> list:
        """Generate recommendations based on usage patterns"""
        recommendations = []
        
        for provider_name, stats in self.stats.items():
            if stats['calls'] == 0:
                continue
            
            failure_rate = stats['failures'] / stats['calls']
            rate_limit_rate = stats['rate_limits'] / stats['calls']
            
            if rate_limit_rate > 0.3:
                recommendations.append(
                    f"{provider_name}: High rate limit rate ({rate_limit_rate:.1%}). "
                    f"Consider reducing max_iter or using Groq for iteration-heavy tasks."
                )
            
            if failure_rate > 0.2 and rate_limit_rate < 0.1:
                recommendations.append(
                    f"{provider_name}: High failure rate ({failure_rate:.1%}) but not rate limits. "
                    f"Check API key or service status."
                )
        
        return recommendations
    
    def display_statistics(self):
        """Display statistics in formatted table"""
        from rich.table import Table
        
        console.print("\n[bold cyan]LLM Manager Statistics:[/bold cyan]\n")
        
        table = Table(show_header=True)
        table.add_column("Provider", style="cyan")
        table.add_column("Calls", justify="right", style="yellow")
        table.add_column("Success", justify="right", style="green")
        table.add_column("Failures", justify="right", style="red")
        table.add_column("Rate Limits", justify="right", style="yellow")
        table.add_column("Success Rate", justify="right")
        
        for provider_name, stats in self.stats.items():
            if stats['calls'] > 0:
                success_rate = stats['successes'] / stats['calls'] * 100
                table.add_row(
                    provider_name,
                    str(stats['calls']),
                    str(stats['successes']),
                    str(stats['failures']),
                    str(stats['rate_limits']),
                    f"{success_rate:.1f}%"
                )
        
        console.print(table)
        
        # Recommendations
        recommendations = self._generate_recommendations()
        if recommendations:
            console.print("\n[bold cyan]Recommendations:[/bold cyan]")
            for rec in recommendations:
                console.print(f"  • {rec}")
        
        console.print()


# Global singleton instance
_llm_manager = None

def get_llm_manager() -> LLMManager:
    """Get or create LLM manager singleton"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager