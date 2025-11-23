"""
Metrics Collection and Tracking
Updated for Free LLM Stack (Gemini, Groq, Ollama)
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class AgentMetrics:
    """Metrics for a single agent execution"""
    agent_name: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    llm_provider: str = "unknown"  # gemini, groq, or ollama
    tokens_used: int = 0  # Estimated, not all providers report this
    error: Optional[str] = None


@dataclass
class GenerationMetrics:
    """Metrics for complete content generation"""
    topic: str
    total_duration: float
    agent_metrics: List[AgentMetrics]
    total_tokens: int
    llm_providers_used: Dict[str, int]  # Count of each provider usage
    estimated_cost: float  # Always $0 for free providers!
    success: bool
    timestamp: str


class MetricsCollector:
    """Collect and track performance metrics for content generation"""
    
    def __init__(self):
        self.agent_metrics: List[AgentMetrics] = []
        self.start_time: Optional[float] = None
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
        
    def start_generation(self):
        """Mark start of content generation"""
        self.start_time = time.time()
        self.agent_metrics = []
    
    def track_agent(self, agent_name: str, success: bool, 
                   llm_provider: str = "unknown", tokens: int = 0, error: str = None):
        """
        Track individual agent performance
        
        Args:
            agent_name: Name of the agent
            success: Whether execution succeeded
            llm_provider: Which LLM was used (gemini, groq, ollama)
            tokens: Estimated token count
            error: Error message if failed
        """
        end_time = time.time()
        start = self.start_time if self.start_time else end_time
        
        metric = AgentMetrics(
            agent_name=agent_name,
            start_time=start,
            end_time=end_time,
            duration=end_time - start,
            success=success,
            llm_provider=llm_provider.lower(),
            tokens_used=tokens,
            error=error
        )
        self.agent_metrics.append(metric)
    
    def finalize(self, topic: str, success: bool) -> GenerationMetrics:
        """
        Generate final metrics report
        
        Args:
            topic: Topic of the generated content
            success: Overall success status
            
        Returns:
            Complete metrics report
        """
        total_duration = time.time() - (self.start_time or time.time())
        total_tokens = sum(m.tokens_used for m in self.agent_metrics)
        
        # Count provider usage
        provider_usage = {}
        for metric in self.agent_metrics:
            provider = metric.llm_provider
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        # Cost is ALWAYS $0 for free LLM providers!
        estimated_cost = 0.0
        
        metrics = GenerationMetrics(
            topic=topic,
            total_duration=total_duration,
            agent_metrics=self.agent_metrics,
            total_tokens=total_tokens,
            llm_providers_used=provider_usage,
            estimated_cost=estimated_cost,
            success=success,
            timestamp=datetime.now().isoformat()
        )
        
        self.save_metrics(metrics)
        return metrics
    
    def save_metrics(self, metrics: GenerationMetrics):
        """Save metrics to file"""
        metrics_file = self.metrics_dir / 'generation_metrics.jsonl'
        
        with open(metrics_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(metrics), default=str) + '\n')
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        if not self.agent_metrics:
            return "No metrics collected"
        
        report = "\n" + "="*70 + "\n"
        report += "PERFORMANCE METRICS REPORT\n"
        report += "="*70 + "\n\n"
        
        # Individual agent metrics
        for metric in self.agent_metrics:
            status = "✅ SUCCESS" if metric.success else "❌ FAILED"
            report += f"{metric.agent_name}:\n"
            report += f"  Duration: {metric.duration:.2f}s\n"
            report += f"  LLM Provider: {metric.llm_provider.upper()}\n"
            if metric.tokens_used > 0:
                report += f"  Tokens: ~{metric.tokens_used}\n"
            report += f"  Status: {status}\n"
            if metric.error:
                report += f"  Error: {metric.error}\n"
            report += "\n"
        
        # Calculate totals
        total_duration = sum(m.duration for m in self.agent_metrics)
        total_tokens = sum(m.tokens_used for m in self.agent_metrics)
        
        # Provider usage breakdown
        provider_counts = {}
        for metric in self.agent_metrics:
            provider = metric.llm_provider
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        report += "-"*70 + "\n"
        report += "TOTALS:\n"
        report += f"  Total Duration: {total_duration:.2f}s\n"
        if total_tokens > 0:
            report += f"  Total Tokens: ~{total_tokens}\n"
        
        report += f"\n  LLM Provider Usage:\n"
        for provider, count in provider_counts.items():
            report += f"    {provider.upper()}: {count} calls\n"
        
        report += f"\n  💰 Total Cost: $0.00 (FREE!)\n"
        report += "="*70 + "\n"
        
        return report
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        if not self.agent_metrics:
            return {
                "total_agents": 0,
                "successful_agents": 0,
                "failed_agents": 0,
                "total_duration": 0,
                "total_tokens": 0,
                "cost": 0.0
            }
        
        return {
            "total_agents": len(self.agent_metrics),
            "successful_agents": sum(1 for m in self.agent_metrics if m.success),
            "failed_agents": sum(1 for m in self.agent_metrics if not m.success),
            "total_duration": sum(m.duration for m in self.agent_metrics),
            "total_tokens": sum(m.tokens_used for m in self.agent_metrics),
            "cost": 0.0,  # Always free!
            "providers_used": {m.llm_provider for m in self.agent_metrics}
        }


class SessionMetrics:
    """Track metrics across multiple generation sessions"""
    
    def __init__(self):
        self.metrics_dir = Path("metrics")
        self.metrics_dir.mkdir(exist_ok=True)
    
    def load_all_metrics(self) -> List[GenerationMetrics]:
        """Load all saved metrics"""
        metrics_file = self.metrics_dir / 'generation_metrics.jsonl'
        
        if not metrics_file.exists():
            return []
        
        metrics_list = []
        with open(metrics_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    # Reconstruct dataclass (simplified)
                    metrics_list.append(data)
        
        return metrics_list
    
    def generate_session_report(self, last_n: int = 10) -> str:
        """Generate report for last N sessions"""
        all_metrics = self.load_all_metrics()
        
        if not all_metrics:
            return "No metrics available"
        
        recent = all_metrics[-last_n:] if len(all_metrics) > last_n else all_metrics
        
        report = "\n" + "="*70 + "\n"
        report += f"SESSION REPORT (Last {len(recent)} generations)\n"
        report += "="*70 + "\n\n"
        
        total_duration = sum(m['total_duration'] for m in recent)
        total_tokens = sum(m['total_tokens'] for m in recent)
        successful = sum(1 for m in recent if m['success'])
        
        report += f"Total Generations: {len(recent)}\n"
        report += f"Successful: {successful} ({successful/len(recent)*100:.1f}%)\n"
        report += f"Failed: {len(recent) - successful}\n"
        report += f"Average Duration: {total_duration/len(recent):.2f}s\n"
        report += f"Total Tokens: ~{total_tokens}\n"
        report += f"💰 Total Cost: $0.00 (100% FREE!)\n"
        report += "="*70 + "\n"
        
        return report


# Create global collector instance
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector singleton"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector