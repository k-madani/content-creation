"""
Content Creation System - Complete with Feedback Loop + Multimodal Integration
FIXED: Added return statement in generate_single_attempt
"""
import warnings
import fix_signals
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*Python version.*")

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from crewai import Crew, Process
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
import time
import re

from agents.content_agents import content_agents
from tasks.content_tasks import content_tasks
from tools.research_tool import research_tool
from tools.seo_optimizer import seo_optimizer
from tools.tone_analyzer import tone_analyzer
from tools.image_generator import ImageGenerator
from utils.user_input import UserInputCollector
from utils.progress_tracker import ContentProgressTracker
from utils.quality_scorer import quality_scorer
from utils.shared_memory import shared_memory
from utils.feedback_loop import feedback_loop

load_dotenv()
console = Console()


def generate_single_attempt(config, attempt_num):
    """Single generation attempt with clean output"""
    
    tracker = ContentProgressTracker()
    tracker.start_tracking()
    
    console.print("\n[dim]Initializing agents...[/dim]")
    research_agent = content_agents.research_agent([research_tool])
    writer_agent = content_agents.writer_agent([tone_analyzer])
    editor_agent = content_agents.editor_agent([tone_analyzer])
    seo_agent = content_agents.seo_agent([seo_optimizer, tone_analyzer])
    console.print("[green]✓[/green] Ready\n")
    
    console.print("[dim]Creating tasks...[/dim]")
    research_task = content_tasks.research_task(
        research_agent,
        config['topic'],
        f"{config.get('audience', 'general audience')} with {config['tone']} tone"
    )
    
    writing_task = content_tasks.writing_task(
        writer_agent,
        research_task,
        config.get('content_type', 'blog post'),
        config['word_count']
    )
    
    editing_task = content_tasks.editing_task(editor_agent, writing_task)
    
    seo_task = content_tasks.seo_optimization_task(
        seo_agent,
        editing_task,
        config.get('keywords', [])
    )
    console.print("[green]✓[/green] Ready\n")
    
    crew = Crew(
        agents=[research_agent, writer_agent, editor_agent, seo_agent],
        tasks=[research_task, writing_task, editing_task, seo_task],
        process=Process.sequential,
        verbose=False  
    )
    
    try:
        console.print(f"\n[cyan]⏳ Generating (Attempt {attempt_num})...[/cyan]")
        console.print("[dim]This takes approximately few minutes[/dim]\n")   
        
        # Simple 1-line progress updates
        console.print("[cyan]🔍 Research...[/cyan]", end=" ")
        
        # Execute crew (runs all agents)
        result = crew.kickoff()
        
        # Simple completion messages
        console.print("[green]✓[/green]")
        console.print("[cyan]✍️  Writing...[/cyan]", end=" ")
        console.print("[green]✓[/green]")
        console.print("[cyan]✨ Editing...[/cyan]", end=" ")
        console.print("[green]✓[/green]")
        console.print("[cyan]🎯 SEO...[/cyan]", end=" ")
        console.print("[green]✓[/green]\n")
        
        # CRITICAL FIX: Return the result!
        return result

    except Exception as e:
        console.print(f"\n[red]✗ Failed: {str(e)[:100]}[/red]\n")
        shared_memory.log_error('generation_failure', str(e), f'Attempt {attempt_num} failed')
        return None


def create_content_with_config(config: dict):
    """Generate content with feedback loop"""
    
    console.print("\n" + "="*60, style="bold")
    console.print("🚀 CONTENT GENERATION WITH FEEDBACK LOOP", style="bold cyan")
    if config.get('include_images', False):
        console.print("🎨 MULTIMODAL MODE: Text + Image Generation", style="bold magenta")
    console.print("="*60 + "\n", style="bold")
    
    shared_memory.store('user_preferences', config, 'System')
    feedback_loop.reset()
    
    quality_threshold = config.get('quality_threshold', 75)
    max_attempts = 2
    
    best_content = None
    best_score = 0
    best_quality_data = None
    
    # FEEDBACK LOOP
    for attempt in range(1, max_attempts + 1):
        
        console.print(f"\n[bold]{'='*60}[/bold]")
        console.print(f"[bold cyan]📝 ATTEMPT {attempt}/{max_attempts}[/bold cyan]")
        console.print(f"[bold]{'='*60}[/bold]\n")
        
        content = generate_single_attempt(config, attempt)
        
        if not content:
            console.print(f"[red]❌ Attempt {attempt} failed[/red]\n")
            if attempt < max_attempts:
                console.print("[yellow]⏳ Waiting 30s...[/yellow]\n")
                time.sleep(30)
                continue
            break
        
        # Evaluate quality
        console.print("\n[cyan]📊 Evaluating quality...[/cyan]\n")
        
        quality_data = quality_scorer.evaluate_content(
            str(content),
            config['word_count'],
            config.get('keywords', [])
        )
        
        shared_memory.add_quality_score(attempt, quality_data['overall_score'], {
            'structure': quality_data['structure_score'],
            'completeness': quality_data['completeness_score'],
            'readability': quality_data['readability_score'],
            'seo': quality_data['seo_score']
        })
        
        quality_scorer.display_quality_report(quality_data)
        
        if quality_data['overall_score'] > best_score:
            best_content = content
            best_score = quality_data['overall_score']
            best_quality_data = quality_data
        
        issues, improvements = feedback_loop.analyze_issues(quality_data)
        feedback_loop.record_attempt(attempt, quality_data['overall_score'], quality_data['grade'], issues)
        
        if not feedback_loop.should_regenerate(quality_data['overall_score'], quality_threshold, attempt):
            break
        
        if attempt < max_attempts:
            should_retry = Confirm.ask(
                f"\n[yellow]Retry with improvements?[/yellow]",
                default=True
            )
            
            if not should_retry:
                break
            
            if improvements:
                console.print(f"\n[cyan]💡 Applying improvements:[/cyan]")
                for key, value in improvements.items():
                    if key == 'word_count':
                        config[key] = value
                        console.print(f"  → Word count: {value}")
                console.print()
            console.print("[dim]⏳ Waiting 60s to avoid rate limits...[/dim]\n")
            time.sleep(60)
    
    feedback_loop.display_history()
    
    if not best_content:
        console.print("[red]❌ Generation failed[/red]\n")
        return None
    
    # Save
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    safe_filename = re.sub(r'[^\w\s-]', '', config['topic']).strip().replace(' ', '_')[:50]
    filepath = output_dir / f"{safe_filename}.md"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(best_content))
    
    console.print(f"[green]✓[/green] Saved to: {filepath}\n")
    
    # Statistics
    console.print("\n[bold cyan]📈 FINAL STATISTICS:[/bold cyan]\n")
    
    word_count = len(str(best_content).split())
    word_diff = word_count - config['word_count']
    
    stats_table = Table(show_header=False, box=None)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("📏 Words", f"{word_count}")
    stats_table.add_row("🎯 Target", f"{config['word_count']}")
    stats_table.add_row("📊 Diff", f"{word_diff:+d} ({word_diff/config['word_count']*100:+.1f}%)")
    stats_table.add_row("⭐ Score", f"{best_score}/100 ({best_quality_data['grade']})")
    stats_table.add_row("🔄 Attempts", f"{len(feedback_loop.attempt_history)}")
    
    # Add image stats if generated
    if config.get('include_images', False):
        images = shared_memory.retrieve('generated_images', [])
        stats_table.add_row("🖼️  Images", f"{len(images)}/{config.get('image_count', 0)}")
    
    stats_table.add_row("💾 File", str(filepath))
    stats_table.add_row("💰 Cost", "$0.00")
    
    console.print(stats_table)
    
    # Memory summary
    shared_memory.display_summary()
    
    if best_score >= quality_threshold:
        console.print(f"[bold green]✅ Quality threshold met[/bold green]\n")
    else:
        console.print(f"[bold yellow]⚠️  Best possible result[/bold yellow]\n")
    
    return best_content


def main():
    """Main entry point"""
    
    console.print("\n[bold cyan]╔═══════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║  AI CONTENT GENERATION SYSTEM         ║[/bold cyan]")
    console.print("[bold cyan]║  Multimodal: Text + Image Generation  ║[/bold cyan]")
    console.print("[bold cyan]╚═══════════════════════════════════════╝[/bold cyan]\n")
    
    try:
        console.print("[bold]Select Mode:[/bold]")
        console.print("1. Express - Just topic")
        console.print("2. Guided - Step-by-step")
        console.print("3. Custom - Full control\n")
        
        mode_choice = Prompt.ask("Mode", choices=["1", "2", "3"], default="2")
        mode_map = {"1": "express", "2": "guided", "3": "custom"}
        
        collector = UserInputCollector()
        config = collector.collect_all_inputs(mode_map[mode_choice])
        
        if not Confirm.ask("\n[yellow]Generate?[/yellow]", default=True):
            console.print("[red]Cancelled[/red]\n")
            return
        
        result = create_content_with_config(config)
        
        if result:
            console.print("\n[bold green]🎉 COMPLETE![/bold green]\n")
            
            if Confirm.ask("[yellow]Generate another?[/yellow]", default=False):
                shared_memory.clear()
                feedback_loop.reset()
                main()
        else:
            console.print("\n[red]❌ Failed[/red]\n")
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Interrupted[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()