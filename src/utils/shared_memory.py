"""
Shared Memory System - Complete Implementation
Provides persistent memory accessible to all agents
"""

import json
from pathlib import Path
from datetime import datetime
from rich.console import Console

console = Console()


class SharedMemory:
    """Shared knowledge base for all agents with persistence"""
    
    def __init__(self, session_id=None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.memory = {
            'session_id': self.session_id,
            'user_preferences': {},
            'research_findings': {},
            'selected_title': '',
            'content_versions': [],
            'quality_scores': [],
            'agent_decisions': [],
            'tool_usage': [],
            'errors_encountered': [],
            'generation_metadata': {
                'total_attempts': 0,
                'successful_generations': 0,
                'average_quality': 0
            }
        }
        
        self.memory_dir = Path("memory")
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / f"session_{self.session_id}.json"
    
    def store(self, key, value, agent_name=None):
        """Store information with tracking"""
        self.memory[key] = value
        
        if agent_name:
            self.memory['agent_decisions'].append({
                'timestamp': datetime.now().isoformat(),
                'agent': agent_name,
                'key': key,
                'value_preview': str(value)[:100]
            })
        
        self._save()
    
    def retrieve(self, key, default=None):
        """Retrieve information from memory"""
        return self.memory.get(key, default)
    
    def add_content_version(self, stage, content, quality_score=None):
        """Track content evolution"""
        version = {
            'timestamp': datetime.now().isoformat(),
            'stage': stage,
            'word_count': len(str(content).split()),
            'preview': str(content)[:200] + "...",
            'quality_score': quality_score
        }
        
        self.memory['content_versions'].append(version)
        self._save()
    
    def add_quality_score(self, attempt, score, breakdown):
        """Track quality scores"""
        self.memory['quality_scores'].append({
            'timestamp': datetime.now().isoformat(),
            'attempt': attempt,
            'overall_score': score,
            'breakdown': breakdown
        })
        
        scores = [s['overall_score'] for s in self.memory['quality_scores']]
        self.memory['generation_metadata']['average_quality'] = sum(scores) / len(scores)
        
        self._save()
    
    def log_error(self, error_type, error_msg, recovery_action):
        """Log errors for analysis"""
        self.memory['errors_encountered'].append({
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': str(error_msg)[:200],
            'recovery_action': recovery_action
        })
        self._save()
    
    def log_tool_usage(self, tool_name, success, execution_time=0):
        """Track tool performance"""
        self.memory['tool_usage'].append({
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'success': success,
            'execution_time': execution_time
        })
        self._save()
    
    def get_context_for_agent(self, agent_role):
        """Provide relevant context to each agent"""
        base_context = {
            'session_id': self.session_id,
            'user_preferences': self.memory['user_preferences']
        }
        
        if agent_role == 'research':
            base_context['topic'] = self.memory['user_preferences'].get('topic')
        elif agent_role == 'writer':
            base_context.update({
                'research': self.memory.get('research_findings'),
                'title': self.memory.get('selected_title')
            })
        elif agent_role == 'editor':
            versions = [v for v in self.memory['content_versions'] if v['stage'] == 'writing']
            base_context['draft'] = versions[-1] if versions else None
        elif agent_role == 'seo':
            base_context['keywords'] = self.memory['user_preferences'].get('keywords')
        
        return base_context
    
    def _save(self):
        """Persist memory to disk"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, default=str)
        except:
            pass
    
    def get_summary(self):
        """Get memory summary"""
        return {
            'session_id': self.session_id,
            'content_versions': len(self.memory['content_versions']),
            'quality_scores': len(self.memory['quality_scores']),
            'agent_decisions': len(self.memory['agent_decisions']),
            'tool_calls': len(self.memory['tool_usage']),
            'errors': len(self.memory['errors_encountered']),
            'average_quality': self.memory['generation_metadata']['average_quality']
        }
    
    def display_summary(self):
        """Display memory summary"""
        from rich.table import Table
        
        summary = self.get_summary()
        
        console.print("\n[bold cyan]Shared Memory Summary:[/bold cyan]")
        
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Content Versions", str(summary['content_versions']))
        table.add_row("Quality Scores", str(summary['quality_scores']))
        table.add_row("Agent Decisions", str(summary['agent_decisions']))
        table.add_row("Tool Calls", str(summary['tool_calls']))
        if summary['average_quality'] > 0:
            table.add_row("Avg Quality", f"{summary['average_quality']:.1f}/100")
        table.add_row("Memory File", str(self.memory_file))
        
        console.print(table)
        console.print()
    
    def clear(self):
        """Clear memory for new generation"""
        old_history = self.memory.get('generation_metadata', {})
        self.__init__()
        self.memory['generation_metadata'] = old_history


# Global instance
shared_memory = SharedMemory()