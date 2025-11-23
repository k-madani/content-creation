"""
User Input Collection System
Handles interactive input with smart defaults
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from tools.title_generator import generate_titles, get_best_title
import re

console = Console()


class UserInputCollector:
    """Collect and validate user input"""
    
    def __init__(self):
        self.config = {}
    
    def collect_all_inputs(self, mode="guided"):
        """
        Collect all necessary inputs from user
        
        Args:
            mode: 'express', 'guided', or 'custom'
        """
        console.print("\n[bold cyan]🚀 CONTENT CREATION SYSTEM[/bold cyan]")
        console.print("[dim]Free LLM Stack (Gemini/Groq)[/dim]\n")
        
        if mode == "express":
            return self._collect_express_mode()
        elif mode == "guided":
            return self._collect_guided_mode()
        else:
            return self._collect_custom_mode()
    
    def _collect_guided_mode(self):
        """Guided mode with recommendations"""
        
        # 1. Get Topic (Required)
        console.print("[bold yellow]Step 1: Topic[/bold yellow]")
        topic = Prompt.ask("📝 What topic do you want to write about?")
        
        while len(topic) < 5:
            console.print("[red]Topic too short. Please be more specific.[/red]")
            topic = Prompt.ask("📝 What topic do you want to write about?")
        
        # 2. Get Tone (With suggestions)
        console.print("\n[bold yellow]Step 2: Tone[/bold yellow]")
        console.print("[dim]Choose the writing style for your content[/dim]")
        
        tone_options = ["professional", "casual", "technical", "conversational"]
        tone_table = Table(show_header=False)
        tone_table.add_column("Option", style="cyan")
        tone_table.add_column("Description", style="dim")
        
        tone_table.add_row("1. Professional", "Business-like, credible, informative")
        tone_table.add_row("2. Casual", "Friendly, conversational, approachable")
        tone_table.add_row("3. Technical", "Expert-level, detailed, precise")
        tone_table.add_row("4. Conversational", "Engaging, personal, relatable")
        
        console.print(tone_table)
        
        tone_choice = Prompt.ask(
            "Select tone",
            choices=["1", "2", "3", "4"],
            default="1"
        )
        
        tone_map = {"1": "professional", "2": "casual", "3": "technical", "4": "conversational"}
        tone = tone_map[tone_choice]
        
        console.print(f"[green]✓[/green] Selected: {tone.capitalize()}\n")
        
        # 3. Generate Title Options
        console.print("[bold yellow]Step 3: Title[/bold yellow]")
        console.print("[dim]Generating title options...[/dim]")
        
        # Generate titles
        title_result = generate_titles(topic, tone, 5)
        
        # Parse the result to extract titles
        titles = self._parse_title_results(title_result)
        
        # Display title options
        console.print("\n[bold cyan]📋 Generated Title Options:[/bold cyan]\n")
        
        title_table = Table(show_header=True)
        title_table.add_column("#", style="cyan", width=3)
        title_table.add_column("Title", style="white")
        title_table.add_column("Score", justify="right", style="yellow")
        
        for i, t in enumerate(titles[:5], 1):
            marker = "⭐" if i == 1 else ""
            title_table.add_row(str(i), f"{marker} {t['title']}", f"{t['score']}/100")
        
        console.print(title_table)
        
        # User selects title
        console.print("\n[dim]Select a title or provide your own[/dim]")
        title_choice = Prompt.ask(
            "Choose title",
            choices=["1", "2", "3", "4", "5", "custom"],
            default="1"
        )
        
        if title_choice == "custom":
            final_title = Prompt.ask("✍️  Enter your custom title")
        else:
            final_title = titles[int(title_choice) - 1]['title']
        
        console.print(f"[green]✓[/green] Selected: \"{final_title}\"\n")
        
        # 4. Additional Options (Optional)
        console.print("[bold yellow]Step 4: Additional Options[/bold yellow]")
        
        word_count = Prompt.ask(
            "Target word count",
            default="1200"
        )
        
        include_images = Confirm.ask(
            "Include images?",
            default=True
        )
        
        if include_images:
            image_count = Prompt.ask(
                "How many images?",
                choices=["1", "2", "3", "4", "5"],
                default="3"
            )
        else:
            image_count = 0
        
        keywords = Prompt.ask(
            "Keywords (comma-separated, optional)",
            default=""
        )
        
        # Build config
        self.config = {
            'topic': topic,
            'tone': tone,
            'title': final_title,
            'word_count': int(word_count),
            'include_images': include_images,
            'image_count': int(image_count) if include_images else 0,
            'keywords': [k.strip() for k in keywords.split(',')] if keywords else []
        }
        
        # Show summary
        self._display_config_summary()
        
        return self.config

    def _collect_custom_mode(self):
        """Custom mode - full control over all parameters"""
        
        console.print("[bold red]⚙️  CUSTOM MODE[/bold red]")
        console.print("[dim]Full control over all parameters[/dim]\n")
        
        # 1. Topic
        topic = Prompt.ask("📝 Topic")
        
        while len(topic) < 5:
            console.print("[red]Topic too short. Please be more specific.[/red]")
            topic = Prompt.ask("📝 Topic")
        
        # 2. Audience
        audience = Prompt.ask(
            "👥 Target Audience",
            default="general audience"
        )
        
        # 3. Tone
        console.print("\n[bold]Tone Options:[/bold]")
        tone = Prompt.ask(
            "🎭 Tone",
            choices=["professional", "casual", "technical", "conversational", "formal"],
            default="professional"
        )
        
        # 4. Content Type
        content_type = Prompt.ask(
            "📄 Content Type",
            choices=["blog post", "article", "guide", "listicle", "review"],
            default="blog post"
        )
        
        # 5. Word Count
        word_count = Prompt.ask(
            "📏 Word Count",
            default="1200"
        )
        
        while not word_count.isdigit() or int(word_count) < 100:
            console.print("[red]Invalid word count. Must be at least 100.[/red]")
            word_count = Prompt.ask("📏 Word Count", default="1200")
        
        # 6. Title Generation or Custom
        console.print("\n[bold]Title Options:[/bold]")
        title_mode = Prompt.ask(
            "📌 Title",
            choices=["generate", "custom"],
            default="generate"
        )
        
        if title_mode == "generate":
            console.print("[dim]Generating title options...[/dim]")
            title_result = generate_titles(topic, tone, 5)
            titles = self._parse_title_results(title_result)
            
            # Display options
            console.print("\n[cyan]Generated Titles:[/cyan]")
            for i, t in enumerate(titles[:5], 1):
                console.print(f"{i}. \"{t['title']}\" ({t['score']}/100)")
            
            title_choice = Prompt.ask(
                "\nSelect title",
                choices=["1", "2", "3", "4", "5"],
                default="1"
            )
            final_title = titles[int(title_choice) - 1]['title']
        else:
            final_title = Prompt.ask("✍️  Enter your title")
        
        console.print(f"[green]✓[/green] Title: \"{final_title}\"\n")
        
        # 7. Images
        include_images = Confirm.ask(
            "🖼️  Include images?",
            default=False
        )
        
        if include_images:
            image_count = Prompt.ask(
                "   How many images?",
                choices=["1", "2", "3", "4", "5"],
                default="2"
            )
        else:
            image_count = 0
        
        # 8. Keywords
        keywords = Prompt.ask(
            "🔑 SEO Keywords (comma-separated, optional)",
            default=""
        )
        
        # 9. Quality threshold
        quality_threshold = Prompt.ask(
            "🎯 Minimum Quality Score (70-90)",
            default="75"
        )
        
        # Build config
        self.config = {
            'topic': topic,
            'audience': audience,
            'tone': tone,
            'content_type': content_type,
            'title': final_title,
            'word_count': int(word_count),
            'include_images': include_images,
            'image_count': int(image_count) if include_images else 0,
            'keywords': [k.strip() for k in keywords.split(',')] if keywords else [],
            'quality_threshold': int(quality_threshold)
        }
        
        # Show summary
        self._display_config_summary()
        
        return self.config
    
    def _collect_express_mode(self):
        """Express mode - just topic, auto everything else"""
        
        console.print("[bold cyan]⚡ EXPRESS MODE[/bold cyan]")
        console.print("[dim]Just provide a topic, we'll handle the rest![/dim]\n")
        
        topic = Prompt.ask("📝 Topic")
        
        # Auto-detect tone from topic
        tone = self._auto_detect_tone(topic)
        console.print(f"[dim]→ Auto-detected tone: {tone}[/dim]")
        
        # Auto-generate best title
        title = get_best_title(topic, tone)
        console.print(f"[dim]→ Auto-generated title: \"{title}\"[/dim]")
        
        self.config = {
            'topic': topic,
            'tone': tone,
            'title': title,
            'word_count': 1200,
            'include_images': True,
            'image_count': 3,
            'keywords': []
        }
        
        console.print("[green]✓ Configuration ready![/green]\n")
        
        return self.config
    
    def _auto_detect_tone(self, topic):
        """Auto-detect appropriate tone from topic"""
        
        topic_lower = topic.lower()
        
        # Technical topics
        if any(word in topic_lower for word in ['algorithm', 'machine learning', 'quantum', 'programming', 'technical']):
            return 'technical'
        
        # Casual topics
        if any(word in topic_lower for word in ['coffee', 'food', 'travel', 'lifestyle', 'best', 'fun']):
            return 'casual'
        
        # Default to professional
        return 'professional'
    
    def _parse_title_results(self, title_result):
        """Parse title generation results into list"""
        
        titles = []
        lines = title_result.split('\n')
        
        for line in lines:
            # Look for numbered titles
            match = re.match(r'(\d+)\.\s+"([^"]+)"', line)
            if match:
                num = match.group(1)
                title_text = match.group(2)
                
                # Find score in next few lines
                score = 50  # default
                idx = lines.index(line)
                for i in range(idx, min(idx + 5, len(lines))):
                    score_match = re.search(r'Score:\s*(\d+)/100', lines[i])
                    if score_match:
                        score = int(score_match.group(1))
                        break
                
                titles.append({
                    'title': title_text,
                    'score': score
                })
        
        return titles
    
    def _display_config_summary(self):
        """Display final configuration summary"""
        
        console.print("\n[bold green]📋 CONFIGURATION SUMMARY[/bold green]")
        
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Field", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("📝 Topic", self.config['topic'])
        summary_table.add_row("🎭 Tone", self.config['tone'].capitalize())
        summary_table.add_row("📌 Title", f"\"{self.config['title']}\"")
        summary_table.add_row("📏 Word Count", str(self.config['word_count']))
        summary_table.add_row("🖼️  Images", f"Yes ({self.config['image_count']})" if self.config['include_images'] else "No")
        
        if self.config['keywords']:
            summary_table.add_row("🔑 Keywords", ", ".join(self.config['keywords']))
        
        console.print(summary_table)
        console.print()