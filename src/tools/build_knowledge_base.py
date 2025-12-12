"""
Knowledge Base Builder - No ChromaDB
Uses sentence-transformers + NumPy + Pickle only
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import docx
import re
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from typing import List, Dict
import numpy as np
import pickle

console = Console()


class SimpleKnowledgeBaseBuilder:
    """Build knowledge base using sentence-transformers + numpy"""
    
    def __init__(self):
        self.kb_dir = Path("knowledge_base")
        self.kb_dir.mkdir(exist_ok=True)
        
        self.docs_dir = self.kb_dir / "documents"
        self.docs_dir.mkdir(exist_ok=True)
        
        console.print("[cyan]Loading embedding model...[/cyan]")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        console.print("[green]✓ Model loaded[/green]\n")
        
        self.embeddings = []
        self.metadata = []
        
        self.chunk_size = 500
        self.chunk_overlap = 50
    
    def ingest_directory(self, directory: Path = None):
        """Ingest all documents from directory"""
        
        if directory is None:
            directory = self.docs_dir
        
        if not directory.exists():
            console.print(f"[yellow]Directory not found: {directory}[/yellow]")
            return
        
        files = (
            list(directory.glob("**/*.txt")) +
            list(directory.glob("**/*.md")) +
            list(directory.glob("**/*.pdf")) +
            list(directory.glob("**/*.docx"))
        )
        
        if not files:
            console.print(f"[yellow]No documents found[/yellow]")
            console.print("[dim]Creating sample documents...[/dim]\n")
            create_sample_documents()
            files = list(directory.glob("**/*.txt")) + list(directory.glob("**/*.md"))
        
        console.print(f"[cyan]Found {len(files)} documents[/cyan]\n")
        
        all_chunks = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("Processing documents...", total=len(files))
            
            for file in files:
                try:
                    text = self._extract_text(file)
                    
                    if not text or len(text) < 100:
                        progress.console.print(f"[dim]⊘ Skipped {file.name} (too short)[/dim]")
                        progress.advance(task)
                        continue
                    
                    chunks = self._chunk_text(text, file)
                    all_chunks.extend(chunks)
                    
                    progress.console.print(f"[green]✓ {file.name}[/green] ({len(chunks)} chunks)")
                    
                except Exception as e:
                    progress.console.print(f"[red]✗ {file.name}: {str(e)[:60]}[/red]")
                
                progress.advance(task)
        
        if all_chunks:
            console.print(f"\n[cyan]Generating embeddings for {len(all_chunks)} chunks...[/cyan]")
            self._add_chunks(all_chunks)
            self._save()
            console.print(f"[green]✓ Knowledge base saved[/green]\n")
            self._display_stats()
        else:
            console.print("[red]No chunks created[/red]\n")
    
    def _chunk_text(self, text: str, file: Path) -> List[Dict]:
        """Chunk text with overlap"""
        
        text = re.sub(r'\s+', ' ', text).strip()
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text.split()) >= 50:
                chunks.append({
                    'text': chunk_text,
                    'source': file.name,
                    'topic': self._infer_topic(file.name, chunk_text),
                    'chunk_id': len(chunks)
                })
        
        return chunks
    
    def _add_chunks(self, chunks: List[Dict]):
        """Add chunks with embeddings"""
        
        texts = [c['text'] for c in chunks]
        embeddings = self.embedder.encode(texts, show_progress_bar=True)
        
        self.embeddings = embeddings
        self.metadata = chunks
    
    def _save(self):
        """Save to disk"""
        
        embeddings_path = self.kb_dir / "embeddings.npy"
        metadata_path = self.kb_dir / "metadata.pkl"
        
        np.save(str(embeddings_path), self.embeddings)
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        console.print(f"[green]✓ Saved to {embeddings_path}[/green]")
        console.print(f"[green]✓ Saved to {metadata_path}[/green]")
    
    def _extract_text(self, file: Path) -> str:
        """Extract text from file"""
        
        if file.suffix == '.txt':
            return file.read_text(encoding='utf-8', errors='ignore')
        
        elif file.suffix == '.md':
            return file.read_text(encoding='utf-8', errors='ignore')
        
        elif file.suffix == '.pdf':
            try:
                reader = PdfReader(str(file))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except:
                return ""
        
        elif file.suffix == '.docx':
            try:
                doc = docx.Document(str(file))
                return "\n".join([para.text for para in doc.paragraphs])
            except:
                return ""
        
        return ""
    
    def _infer_topic(self, filename: str, content: str) -> str:
        """Infer topic from filename and content"""
        
        text = (filename + " " + content[:500]).lower()
        
        topics = {
            'Artificial Intelligence': ['ai', 'artificial intelligence', 'machine learning', 'deep learning'],
            'Technology': ['software', 'programming', 'code', 'algorithm', 'tech'],
            'Business': ['business', 'marketing', 'sales', 'strategy'],
            'Health': ['health', 'medical', 'wellness'],
            'Education': ['education', 'learning', 'teaching'],
        }
        
        for topic, keywords in topics.items():
            if any(kw in text for kw in keywords):
                return topic
        
        return 'General'
    
    def _display_stats(self):
        """Display build statistics"""
        
        console.print("\n[bold cyan]════════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]   KNOWLEDGE BASE BUILD COMPLETE[/bold cyan]")
        console.print("[bold cyan]════════════════════════════════════════[/bold cyan]\n")
        
        from collections import Counter
        topics = Counter(m['topic'] for m in self.metadata)
        
        table = Table(title="Build Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow", justify="right")
        
        table.add_row("Total Chunks", str(len(self.metadata)))
        table.add_row("Embedding Dimension", "384")
        table.add_row("Total Words", f"{sum(len(m['text'].split()) for m in self.metadata):,}")
        
        console.print(table)
        
        console.print("\n[bold cyan]Domain Distribution:[/bold cyan]")
        domain_table = Table(show_header=False)
        domain_table.add_column("Domain", style="cyan")
        domain_table.add_column("Chunks", style="yellow", justify="right")
        
        for topic, count in topics.most_common():
            domain_table.add_row(topic, str(count))
        
        console.print(domain_table)
        console.print("\n[green]✓ Ready for RAG retrieval![/green]\n")


def create_sample_documents():
    """Create sample documents"""
    
    kb_dir = Path("knowledge_base/documents")
    kb_dir.mkdir(parents=True, exist_ok=True)
    
    samples = {
        'ai_machine_learning.txt': """Machine Learning and Artificial Intelligence

Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience. Key concepts include supervised learning (training on labeled data), unsupervised learning (finding patterns), and reinforcement learning (learning through trial and error).

Deep learning uses neural networks with multiple layers. CNNs excel at computer vision, RNNs process sequences, and Transformers revolutionized NLP. Applications include image recognition, natural language processing, recommendation systems, and autonomous vehicles.

Challenges include data quality, model interpretability, ethical considerations, and computational requirements. Research continues in few-shot learning, transfer learning, and continual learning.""",
        
        'content_marketing.txt': """Content Marketing Best Practices

Content marketing focuses on creating valuable content to attract and retain audiences. Effective strategies include knowing your audience, creating quality content, maintaining consistency, and optimizing for SEO.

Content types that work: how-to guides, case studies, industry insights, listicles, and original research. Use multiple formats: blog posts, videos, infographics, and podcasts.

Measure success through metrics like page views, time on page, social shares, conversion rates, and lead generation. Track with Google Analytics to understand what resonates with your audience.""",
        
        'software_development.txt': """Modern Software Development Practices

Agile methodologies like Scrum and Kanban promote iterative development and regular feedback. DevOps bridges development and operations through automation, CI/CD pipelines, and infrastructure as code.

Clean code principles: write readable code, follow SOLID principles, use meaningful names, keep functions small, and practice test-driven development.

Testing strategies follow the test pyramid: unit tests (fast, high coverage), integration tests (component interactions), and end-to-end tests (complete user flows).

Architecture patterns include microservices (independent services) and event-driven architecture (asynchronous processing). Version control with Git uses branching strategies and code reviews."""
    }
    
    for filename, content in samples.items():
        filepath = kb_dir / filename
        filepath.write_text(content.strip())
    
    console.print(f"[green]✓ Created {len(samples)} sample documents[/green]")


def main():
    """Main entry point"""
    
    console.print("\n[bold cyan]╔════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║   KNOWLEDGE BASE BUILDER               ║[/bold cyan]")
    console.print("[bold cyan]║   Sentence Transformers + NumPy        ║[/bold cyan]")
    console.print("[bold cyan]╚════════════════════════════════════════╝[/bold cyan]\n")
    
    builder = SimpleKnowledgeBaseBuilder()
    builder.ingest_directory()


if __name__ == "__main__":
    main()