"""
Simple Progress Tracker - No Overlapping Boxes
"""

from rich.console import Console
from rich.table import Table
import time

console = Console()


class ContentProgressTracker:
    """Simple progress tracker without live updates"""
    
    def __init__(self):
        self.stages = {
            'research': {'status': 'pending', 'time': 0, 'icon': '🔍'},
            'writing': {'status': 'pending', 'time': 0, 'icon': '✍️'},
            'editing': {'status': 'pending', 'time': 0, 'icon': '📝'},
            'seo': {'status': 'pending', 'time': 0, 'icon': '🎯'}
        }
        self.start_time = None
        self.current_stage = None
        self.stage_start = None
    
    def start_tracking(self):
        """Start overall tracking"""
        self.start_time = time.time()
    
    def start_stage(self, stage_name):
        """Start a stage - just print, don't update table"""
        self.current_stage = stage_name
        self.stage_start = time.time()
        self.stages[stage_name]['status'] = 'working'
        
        # Simple print instead of table update
        icon = self.stages[stage_name]['icon']
        console.print(f"\n[yellow]{icon} {stage_name.title()} phase starting...[/yellow]")
    
    def complete_stage(self, stage_name):
        """Complete a stage"""
        if self.stage_start:
            elapsed = time.time() - self.stage_start
            self.stages[stage_name]['time'] = elapsed
        
        self.stages[stage_name]['status'] = 'done'
        
        # Simple completion message
        icon = self.stages[stage_name]['icon']
        elapsed_str = f"{self.stages[stage_name]['time']:.1f}s"
        console.print(f"[green]✓ {stage_name.title()} complete ({elapsed_str})[/green]")
    
    def get_completion_summary(self):
        """Get final summary - ONE table at the end"""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        table = Table(title="[cyan]Generation Complete[/cyan]", show_header=True)
        table.add_column("Stage", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Time", style="yellow")
        
        for stage_name, data in self.stages.items():
            icon = data['icon']
            status = "✓ Done" if data['status'] == 'done' else "Pending"
            time_str = f"{data['time']:.1f}s" if data['time'] > 0 else "-"
            
            table.add_row(
                f"{icon} {stage_name.title()}",
                status,
                time_str
            )
        
        table.add_row("", "", "", style="dim")
        table.add_row("[bold]Total[/bold]", "", f"[bold]{total_time:.1f}s[/bold]")
        
        return table