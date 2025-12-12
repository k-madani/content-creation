"""
RAG System Evaluator
Measures retrieval quality, relevance, and performance
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.rag_retrieval_tool import get_retriever
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import time
from typing import List, Dict
import numpy as np

console = Console()


class RAGEvaluator:
    """
    Evaluate RAG system performance across multiple dimensions
    """
    
    def __init__(self):
        self.retriever = get_retriever()
        self.test_queries = self._generate_test_queries()
    
    def _generate_test_queries(self) -> List[Dict]:
        """Generate test queries with expected topics"""
        return [
            {
                'query': 'machine learning applications',
                'expected_domain': 'Artificial Intelligence',
                'min_results': 3
            },
            {
                'query': 'content marketing strategies',
                'expected_domain': 'Business',
                'min_results': 3
            },
            {
                'query': 'software testing best practices',
                'expected_domain': 'Technology',
                'min_results': 2
            },
            {
                'query': 'neural networks deep learning',
                'expected_domain': 'Artificial Intelligence',
                'min_results': 2
            },
            {
                'query': 'agile development methodology',
                'expected_domain': 'Technology',
                'min_results': 2
            }
        ]
    
    def evaluate_retrieval_quality(self) -> Dict:
        """
        Comprehensive evaluation of retrieval quality
        """
        
        console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]   RAG SYSTEM EVALUATION[/bold cyan]")
        console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
        
        metrics = {
            'precision_scores': [],
            'recall_scores': [],
            'relevance_scores': [],
            'latency_ms': [],
            'successful_queries': 0,
            'failed_queries': 0
        }
        
        for test in self.test_queries:
            console.print(f"[cyan]Testing:[/cyan] {test['query']}")
            
            # Measure latency
            start_time = time.time()
            results = self.retriever.hybrid_search(
                query=test['query'],
                n_results=5,
                min_relevance=0.3
            )
            latency = (time.time() - start_time) * 1000  # Convert to ms
            
            metrics['latency_ms'].append(latency)
            
            if not results:
                console.print("  [red]✗ No results returned[/red]\n")
                metrics['failed_queries'] += 1
                continue
            
            # Evaluate precision (relevant results / total results)
            relevant_count = sum(1 for r in results if r['relevance_score'] >= 0.5)
            precision = relevant_count / len(results) if results else 0
            
            # Evaluate recall (found expected domain)
            domain_match = any(
                r.get('topic') == test['expected_domain'] 
                for r in results
            )
            recall = 1.0 if domain_match else 0.5
            
            # Average relevance score
            avg_relevance = np.mean([r['relevance_score'] for r in results])
            
            metrics['precision_scores'].append(precision)
            metrics['recall_scores'].append(recall)
            metrics['relevance_scores'].append(avg_relevance)
            metrics['successful_queries'] += 1
            
            console.print(f"  [green]✓ {len(results)} results[/green] | "
                        f"Precision: {precision:.2f} | "
                        f"Relevance: {avg_relevance:.2f} | "
                        f"Latency: {latency:.1f}ms\n")
        
        # Calculate aggregate metrics
        results = {
            'avg_precision': np.mean(metrics['precision_scores']) if metrics['precision_scores'] else 0,
            'avg_recall': np.mean(metrics['recall_scores']) if metrics['recall_scores'] else 0,
            'avg_relevance': np.mean(metrics['relevance_scores']) if metrics['relevance_scores'] else 0,
            'avg_latency_ms': np.mean(metrics['latency_ms']) if metrics['latency_ms'] else 0,
            'success_rate': metrics['successful_queries'] / len(self.test_queries),
            'total_queries': len(self.test_queries),
            'successful': metrics['successful_queries'],
            'failed': metrics['failed_queries']
        }
        
        self._display_evaluation_results(results)
        
        return results
    
    def evaluate_chunking_quality(self) -> Dict:
        """
        Evaluate chunking strategy effectiveness
        """
        
        console.print("\n[bold cyan]Chunking Quality Analysis:[/bold cyan]\n")
        
        stats = self.retriever.get_stats()
        
        if not self.retriever.metadata:
            console.print("[yellow]No metadata available[/yellow]\n")
            return {}
        
        # Analyze chunk sizes
        chunk_sizes = [m.get('word_count', 0) for m in self.retriever.metadata]
        
        metrics = {
            'total_chunks': len(chunk_sizes),
            'avg_chunk_size': np.mean(chunk_sizes),
            'min_chunk_size': np.min(chunk_sizes),
            'max_chunk_size': np.max(chunk_sizes),
            'std_chunk_size': np.std(chunk_sizes)
        }
        
        # Display distribution
        table = Table(title="Chunk Size Distribution")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow", justify="right")
        
        table.add_row("Total Chunks", str(metrics['total_chunks']))
        table.add_row("Average Size", f"{metrics['avg_chunk_size']:.0f} words")
        table.add_row("Min Size", f"{metrics['min_chunk_size']:.0f} words")
        table.add_row("Max Size", f"{metrics['max_chunk_size']:.0f} words")
        table.add_row("Std Deviation", f"{metrics['std_chunk_size']:.1f} words")
        
        console.print(table)
        console.print()
        
        # Quality assessment
        if 100 <= metrics['avg_chunk_size'] <= 400:
            console.print("[green]✓ Chunk size is optimal for retrieval[/green]\n")
        elif metrics['avg_chunk_size'] < 100:
            console.print("[yellow]⚠ Chunks may be too small for context[/yellow]\n")
        else:
            console.print("[yellow]⚠ Chunks may be too large for precision[/yellow]\n")
        
        return metrics
    
    def evaluate_coverage(self) -> Dict:
        """
        Evaluate knowledge base coverage across domains
        """
        
        console.print("\n[bold cyan]Domain Coverage Analysis:[/bold cyan]\n")
        
        stats = self.retriever.get_stats()
        
        if 'domains' not in stats:
            console.print("[yellow]No domain information available[/yellow]\n")
            return {}
        
        domains = stats['domains']
        total_chunks = sum(domains.values())
        
        table = Table(title="Knowledge Base Coverage")
        table.add_column("Domain", style="cyan")
        table.add_column("Chunks", style="yellow", justify="right")
        table.add_column("Coverage", style="green", justify="right")
        
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_chunks) * 100
            table.add_row(domain, str(count), f"{percentage:.1f}%")
        
        console.print(table)
        console.print()
        
        # Balance assessment
        percentages = [c / total_chunks for c in domains.values()]
        balance_score = 1 - np.std(percentages)
        
        if balance_score > 0.8:
            console.print("[green]✓ Good domain balance[/green]\n")
        else:
            console.print("[yellow]⚠ Consider adding more content to underrepresented domains[/yellow]\n")
        
        return {
            'domains': domains,
            'balance_score': balance_score,
            'total_chunks': total_chunks
        }
    
    def _display_evaluation_results(self, results: Dict):
        """Display evaluation results in formatted tables"""
        
        console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]   EVALUATION RESULTS[/bold cyan]")
        console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
        
        # Performance metrics
        perf_table = Table(title="Retrieval Performance Metrics")
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Score", style="yellow", justify="right")
        perf_table.add_column("Grade", style="green", justify="center")
        
        # Precision
        precision_grade = self._get_grade(results['avg_precision'])
        perf_table.add_row(
            "Precision",
            f"{results['avg_precision']:.2%}",
            precision_grade
        )
        
        # Recall
        recall_grade = self._get_grade(results['avg_recall'])
        perf_table.add_row(
            "Recall",
            f"{results['avg_recall']:.2%}",
            recall_grade
        )
        
        # Relevance
        relevance_grade = self._get_grade(results['avg_relevance'])
        perf_table.add_row(
            "Avg Relevance",
            f"{results['avg_relevance']:.2%}",
            relevance_grade
        )
        
        # Latency
        latency_grade = "🟢 Excellent" if results['avg_latency_ms'] < 100 else "🟡 Good" if results['avg_latency_ms'] < 500 else "🔴 Slow"
        perf_table.add_row(
            "Avg Latency",
            f"{results['avg_latency_ms']:.1f}ms",
            latency_grade
        )
        
        # Success rate
        success_grade = self._get_grade(results['success_rate'])
        perf_table.add_row(
            "Success Rate",
            f"{results['success_rate']:.2%}",
            success_grade
        )
        
        console.print(perf_table)
        console.print()
        
        # Overall assessment
        overall_score = (
            results['avg_precision'] * 0.3 +
            results['avg_recall'] * 0.3 +
            results['avg_relevance'] * 0.4
        )
        
        if overall_score >= 0.8:
            status = "[bold green]EXCELLENT ✓[/bold green]"
            message = "RAG system is performing at high quality standards"
        elif overall_score >= 0.6:
            status = "[bold yellow]GOOD ✓[/bold yellow]"
            message = "RAG system is functional with room for improvement"
        else:
            status = "[bold red]NEEDS IMPROVEMENT ⚠[/bold red]"
            message = "Consider refining chunking strategy or expanding knowledge base"
        
        panel = Panel(
            f"Overall Score: [bold]{overall_score:.1%}[/bold]\n{message}",
            title=f"System Status: {status}",
            border_style="cyan"
        )
        console.print(panel)
        console.print()
    
    def _get_grade(self, score: float) -> str:
        """Convert score to grade"""
        if score >= 0.9:
            return "🟢 Excellent"
        elif score >= 0.75:
            return "🟡 Good"
        elif score >= 0.6:
            return "🟠 Fair"
        else:
            return "🔴 Poor"
    
    def run_full_evaluation(self):
        """Run complete evaluation suite"""
        
        # 1. Retrieval quality
        retrieval_results = self.evaluate_retrieval_quality()
        
        # 2. Chunking quality
        chunking_results = self.evaluate_chunking_quality()
        
        # 3. Coverage analysis
        coverage_results = self.evaluate_coverage()
        
        # Save results
        results_dir = Path("evaluation_results")
        results_dir.mkdir(exist_ok=True)
        
        import json
        with open(results_dir / "rag_evaluation.json", 'w') as f:
            json.dump({
                'retrieval': retrieval_results,
                'chunking': chunking_results,
                'coverage': coverage_results
            }, f, indent=2)
        
        console.print(f"[green]✓ Results saved to {results_dir / 'rag_evaluation.json'}[/green]\n")


def main():
    """Main entry point"""
    
    evaluator = RAGEvaluator()
    evaluator.run_full_evaluation()


if __name__ == "__main__":
    main()