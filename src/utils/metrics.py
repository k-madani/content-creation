import time
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class AgentMetrics:
    """Metrics for a single agent execution"""
    agent_name: str
    start_time: float
    end_time: float
    duration: float
    tokens_used: int
    success: bool
    error: str = None


@dataclass
class GenerationMetrics:
    """Metrics for complete content generation"""
    topic: str
    total_duration: float
    agent_metrics: List[AgentMetrics]
    total_tokens: int
    estimated_cost: float
    success: bool
    timestamp: str


class MetricsCollector:
    """Collect and track performance metrics"""
    
    def __init__(self):
        self.agent_metrics = []
        self.start_time = None
        
    def start_generation(self):
        """Mark start of content generation"""
        self.start_time = time.time()
        self.agent_metrics = []
    
    def track_agent(self, agent_name: str, tokens: int, success: bool, error: str = None):
        """Track individual agent performance"""
        end_time = time.time()
        duration = end_time - (self.start_time or end_time)
        
        metric = AgentMetrics(
            agent_name=agent_name,
            start_time=self.start_time,
            end_time=end_time,
            duration=duration,
            tokens_used=tokens,
            success=success,
            error=error
        )
        self.agent_metrics.append(metric)
    
    def finalize(self, topic: str, success: bool) -> GenerationMetrics:
        """Generate final metrics report"""
        total_duration = time.time() - self.start_time
        total_tokens = sum(m.tokens_used for m in self.agent_metrics)
        
        # Rough cost estimation (GPT-4o-mini pricing)
        estimated_cost = (total_tokens / 1000) * 0.00015  # $0.15 per 1M tokens
        
        metrics = GenerationMetrics(
            topic=topic,
            total_duration=total_duration,
            agent_metrics=self.agent_metrics,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            success=success,
            timestamp=datetime.now().isoformat()
        )
        
        self.save_metrics(metrics)
        return metrics
    
    def save_metrics(self, metrics: GenerationMetrics):
        """Save metrics to file"""
        with open('metrics/generation_metrics.jsonl', 'a') as f:
            f.write(json.dumps(asdict(metrics)) + '\n')
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        if not self.agent_metrics:
            return "No metrics collected"
        
        report = "\n" + "="*70 + "\n"
        report += "PERFORMANCE METRICS REPORT\n"
        report += "="*70 + "\n\n"
        
        for metric in self.agent_metrics:
            status = "SUCCESS" if metric.success else "FAILED"
            report += f"{metric.agent_name}:\n"
            report += f"  Duration: {metric.duration:.2f}s\n"
            report += f"  Tokens: {metric.tokens_used}\n"
            report += f"  Status: {status}\n"
            if metric.error:
                report += f"  Error: {metric.error}\n"
            report += "\n"
        
        total_duration = sum(m.duration for m in self.agent_metrics)
        total_tokens = sum(m.tokens_used for m in self.agent_metrics)
        
        report += f"TOTALS:\n"
        report += f"  Total Duration: {total_duration:.2f}s\n"
        report += f"  Total Tokens: {total_tokens}\n"
        report += f"  Estimated Cost: ${(total_tokens/1000)*0.00015:.4f}\n"
        
        return report