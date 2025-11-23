"""
Real-Time Progress Tracking System
Shows agent execution progress with time estimates
"""

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console
from rich.live import Live
from rich.table import Table
import time
from datetime import datetime

console = Console()


class ContentProgressTracker:
    """Track and display content generation progress"""
    
    def __init__(self):
        self.stages = {
            'research': {'name': '🔍 Research', 'status': 'pending', 'time': 0},
            'writing': {'name': '✍️ Writing', 'status': 'pending', 'time': 0},
            'editing': {'name': '📝 Editing', 'status': 'pending', 'time': 0},
            'seo': {'name': '🎯 SEO', 'status': 'pending', 'time': 0}
        }
        self.current_stage = None
        self.stage_start_time = None
        self.total_start_time = None
    
    def start_tracking(self):
        """Start tracking overall progress"""
        self.total_start_time = time.time()
    
    def start_stage(self, stage_key):
        """Mark stage as started"""
        self.current_stage = stage_key
        self.stage_start_time = time.time()
        self.stages[stage_key]['status'] = 'running'
    
    def complete_stage(self, stage_key):
        """Mark stage as completed"""
        if self.stage_start_time:
            elapsed = time.time() - self.stage_start_time
            self.stages[stage_key]['time'] = elapsed
            self.stages[stage_key]['status'] = 'completed'
    
    def get_progress_table(self):
        """Generate progress table"""
        
        table = Table(title="[bold cyan]Content Generation Progress[/bold cyan]", show_header=True)
        table.add_column("Stage", style="cyan", width=15)
        table.add_column("Status", width=12)
        table.add_column("Time", justify="right", width=10)
        
        for stage_key, stage_data in self.stages.items():
            # Status emoji
            if stage_data['status'] == 'completed':
                status = "[green]✅ Done[/green]"
                time_str = f"{stage_data['time']:.1f}s"
            elif stage_data['status'] == 'running':
                status = "[yellow]⏳ Working...[/yellow]"
                time_str = f"{time.time() - self.stage_start_time:.1f}s" if self.stage_start_time else "-"
            else:
                status = "[dim]⏸️  Pending[/dim]"
                time_str = "-"
            
            table.add_row(stage_data['name'], status, time_str)
        
        # Add total time
        if self.total_start_time:
            total_elapsed = time.time() - self.total_start_time
            table.add_row(
                "[bold]Total[/bold]",
                "",
                f"[bold]{total_elapsed:.1f}s[/bold]"
            )
        
        return table
    
    def get_completion_summary(self):
        """Get final summary after completion"""
        
        total_time = time.time() - self.total_start_time if self.total_start_time else 0
        
        summary = f"""
[bold green]✅ GENERATION COMPLETE![/bold green]

[cyan]⏱️  Performance Summary:[/cyan]
"""
        
        for stage_key, stage_data in self.stages.items():
            if stage_data['status'] == 'completed':
                summary += f"  {stage_data['name']}: {stage_data['time']:.1f}s\n"
        
        summary += f"  [bold]━━━━━━━━━━━━━━━━━━━[/bold]\n"
        summary += f"  [bold]Total Time: {total_time:.1f}s ({total_time/60:.1f} min)[/bold]\n"
        
        return summary


def create_progress_display():
    """Create a live progress display"""
    
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    )
    
    return progress