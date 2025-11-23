"""
Feedback Loop System
Auto-regenerates content if quality threshold not met
"""

from rich.console import Console
from rich.table import Table

console = Console()


class FeedbackLoop:
    """Manages quality-based regeneration"""
    
    def __init__(self, max_attempts=2):
        self.max_attempts = max_attempts
        self.attempt_history = []
    
    def should_regenerate(self, quality_score, threshold, attempt_num):
        """Decide if regeneration needed"""
        
        console.print(f"\n[cyan]Quality Assessment:[/cyan]")
        console.print(f"  Attempt: {attempt_num}/{self.max_attempts}")
        console.print(f"  Score: {quality_score}/100")
        console.print(f"  Threshold: {threshold}/100")
        
        if attempt_num >= self.max_attempts:
            console.print(f"  [yellow]WARNING: Max attempts reached[/yellow]\n")
            return False
        
        if quality_score >= threshold:
            console.print(f"  [green]OK: Meets threshold![/green]\n")
            return False
        
        gap = threshold - quality_score
        console.print(f"  [yellow]WARNING: {gap:.1f} points below threshold[/yellow]\n")
        return True
    
    def analyze_issues(self, quality_data):
        """Analyze quality issues"""
        
        issues = []
        improvements = {}
        
        console.print("[cyan]Analyzing issues...[/cyan]\n")
        
        if quality_data['structure_score'] < 70:
            issues.append("Poor structure")
            console.print("  [yellow]WARNING: Structure - Add more subheaders[/yellow]")
        
        if quality_data['completeness_score'] < 70:
            word_count = quality_data['details']['word_count']
            target = quality_data['details']['target_word_count']
            
            if word_count < target * 0.85:
                issues.append("Too short")
                improvements['word_count'] = int(target * 1.15)
                console.print(f"  [yellow]WARNING: Too short - {word_count} vs {target}[/yellow]")
                console.print(f"  [cyan]INFO: Will target {improvements['word_count']} words[/cyan]")
        
        if quality_data['readability_score'] < 70:
            issues.append("Low readability")
            console.print("  [yellow]WARNING: Readability - Simplify language[/yellow]")
        
        if quality_data['seo_score'] < 70:
            issues.append("Weak SEO")
            console.print("  [yellow]WARNING: SEO - Emphasize keywords[/yellow]")
        
        if not issues:
            console.print("  [green]OK: No critical issues[/green]")
        
        console.print()
        return issues, improvements
    
    def record_attempt(self, attempt_num, quality_score, grade, issues):
        """Record attempt"""
        self.attempt_history.append({
            'attempt': attempt_num,
            'score': quality_score,
            'grade': grade,
            'issues': issues
        })
    
    def display_history(self):
        """Show attempt history"""
        
        if not self.attempt_history:
            return
        
        console.print("\n[bold cyan]Attempt History:[/bold cyan]\n")
        
        table = Table(show_header=True)
        table.add_column("Attempt", style="cyan", width=10)
        table.add_column("Score", justify="right", style="yellow")
        table.add_column("Grade", justify="center", width=12)
        table.add_column("Issues", style="dim")
        
        for record in self.attempt_history:
            issues_str = ", ".join(record['issues']) if record['issues'] else "None"
            marker = "BEST" if record['score'] == max(h['score'] for h in self.attempt_history) else ""
            
            table.add_row(
                f"#{record['attempt']} {marker}",
                f"{record['score']}/100",
                record['grade'],
                issues_str
            )
        
        console.print(table)
        
        if len(self.attempt_history) > 1:
            first = self.attempt_history[0]['score']
            last = self.attempt_history[-1]['score']
            improvement = last - first
            
            if improvement > 0:
                console.print(f"\n[green]Improvement: +{improvement:.1f} points[/green]")
            elif improvement < 0:
                console.print(f"\n[yellow]Decreased: {improvement:.1f} points[/yellow]")
        
        console.print()
    
    def reset(self):
        """Reset for new generation"""
        self.attempt_history = []


# Global instance
feedback_loop = FeedbackLoop(max_attempts=2)