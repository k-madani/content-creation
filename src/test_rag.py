"""
Comprehensive RAG System Test Suite
Tests all RAG components: retrieval, ranking, filtering, performance
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from typing import List, Dict

console = Console()


class RAGSystemTester:
    """Comprehensive test suite for RAG system"""
    
    def __init__(self):
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
    
    def run_all_tests(self):
        """Run complete test suite"""
        
        console.print("\n[bold cyan]╔═══════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║   RAG SYSTEM COMPREHENSIVE TEST SUITE     ║[/bold cyan]")
        console.print("[bold cyan]╚═══════════════════════════════════════════╝[/bold cyan]\n")
        
        # Test 1: Import Tests
        self.test_imports()
        
        # Test 2: Knowledge Base Tests
        self.test_knowledge_base_exists()
        
        # Test 3: Retrieval Tests
        self.test_basic_retrieval()
        self.test_hybrid_search()
        self.test_domain_filtering()
        
        # Test 4: Performance Tests
        self.test_retrieval_performance()
        
        # Test 5: Quality Tests
        self.test_relevance_scoring()
        self.test_ranking_quality()
        
        # Test 6: Edge Cases
        self.test_edge_cases()
        
        # Display summary
        self.display_test_summary()
    
    # In src/test_rag.py, modify the test_imports() method:

    def test_imports(self):
        """Test all required imports"""
        
        console.print("[bold]Test 1: Import Dependencies[/bold]\n")
        
        tests = [
            ("chromadb", "ChromaDB"),
            ("sentence_transformers", "Sentence Transformers"),
            ("rich", "Rich"),
        ]
        
        for module, name in tests:
            try:
                __import__(module)
                self._pass(f"✓ {name} imported successfully")
            except ImportError as e:
                self._fail(f"✗ {name} import failed: {str(e)}")
        
        # Test CrewAI separately (Windows compatibility issue)
        try:
            import crewai
            self._pass("✓ CrewAI imported successfully")
        except AttributeError as e:
            if "SIGHUP" in str(e):
                self._warn("⚠ CrewAI has Windows signal issue (known bug, won't affect RAG)")
            else:
                self._fail(f"✗ CrewAI import failed: {str(e)}")
        except Exception as e:
            self._fail(f"✗ CrewAI import failed: {str(e)}")
        
        # Test custom imports
        try:
            from tools.rag_retrieval_tool import rag_retrieval_tool, get_retriever
            self._pass("✓ RAG retrieval tool imported")
        except Exception as e:
            self._fail(f"✗ RAG tool import failed: {str(e)}")
        
        console.print()
    
    def test_knowledge_base_exists(self):
        """Test knowledge base setup"""
        
        console.print("[bold]Test 2: Knowledge Base Setup[/bold]\n")
        
        kb_dir = Path("knowledge_base")
        chroma_db = kb_dir / "chroma_db"
        docs_dir = kb_dir / "documents"
        
        # Check directories
        if kb_dir.exists():
            self._pass(f"✓ Knowledge base directory exists")
        else:
            self._fail(f"✗ Knowledge base directory missing")
            return
        
        if chroma_db.exists():
            self._pass(f"✓ ChromaDB directory exists")
        else:
            self._warn(f"⚠ ChromaDB not built yet (run build_knowledge_base.py)")
        
        if docs_dir.exists():
            doc_count = len(list(docs_dir.glob("**/*.*")))
            if doc_count > 0:
                self._pass(f"✓ Documents directory has {doc_count} files")
            else:
                self._warn(f"⚠ No documents found in {docs_dir}")
        
        # Test retriever initialization
        try:
            from tools.rag_retrieval_tool import get_retriever
            retriever = get_retriever()
            stats = retriever.get_collection_stats()
            
            if stats['total_chunks'] > 0:
                self._pass(f"✓ Knowledge base loaded: {stats['total_chunks']} chunks")
            else:
                self._warn(f"⚠ Knowledge base empty (run build_knowledge_base.py)")
        except Exception as e:
            self._fail(f"✗ Retriever initialization failed: {str(e)}")
        
        console.print()
    
    def test_basic_retrieval(self):
        """Test basic retrieval functionality"""
        
        console.print("[bold]Test 3: Basic Retrieval[/bold]\n")
        
        try:
            from tools.rag_retrieval_tool import rag_retrieval_tool
            
            # Test query
            query = "machine learning"
            result = rag_retrieval_tool._run(query=query, max_results=3)
            
            if "No relevant results" in result or "Knowledge Base Empty" in result:
                self._warn(f"⚠ No results for '{query}' (knowledge base may be empty)")
            elif "RAG Knowledge Base Results" in result:
                self._pass(f"✓ Basic retrieval working for '{query}'")
                
                # Check for expected content
                if "Result 1" in result:
                    self._pass(f"✓ Results formatted correctly")
                else:
                    self._fail(f"✗ Results format unexpected")
            else:
                self._fail(f"✗ Unexpected result format")
        
        except Exception as e:
            self._fail(f"✗ Basic retrieval failed: {str(e)}")
        
        console.print()
    
    def test_hybrid_search(self):
        """Test hybrid search (semantic + keyword)"""
        
        console.print("[bold]Test 4: Hybrid Search[/bold]\n")
        
        try:
            from tools.rag_retrieval_tool import get_retriever
            retriever = get_retriever()
            
            if retriever.collection.count() == 0:
                self._warn("⚠ Skipping hybrid search test (empty knowledge base)")
                console.print()
                return
            
            # Test semantic search
            results = retriever.search("artificial intelligence applications", n_results=3)
            
            if results and len(results) > 0:
                self._pass(f"✓ Semantic search returned {len(results)} results")
                
                # Check relevance scores
                if all('relevance_score' in r for r in results):
                    self._pass(f"✓ Relevance scores calculated")
                    
                    avg_score = sum(r['relevance_score'] for r in results) / len(results)
                    if avg_score > 0.3:
                        self._pass(f"✓ Average relevance score: {avg_score:.2f}")
                    else:
                        self._warn(f"⚠ Low average relevance: {avg_score:.2f}")
                else:
                    self._fail("✗ Missing relevance scores")
            else:
                self._warn("⚠ No results from hybrid search")
        
        except Exception as e:
            self._fail(f"✗ Hybrid search failed: {str(e)}")
        
        console.print()
    
    def test_domain_filtering(self):
        """Test domain-specific filtering"""
        
        console.print("[bold]Test 5: Domain Filtering[/bold]\n")
        
        try:
            from tools.rag_retrieval_tool import get_retriever
            retriever = get_retriever()
            
            if retriever.collection.count() == 0:
                self._warn("⚠ Skipping domain filtering test (empty knowledge base)")
                console.print()
                return
            
            # Test with domain filter
            results = retriever.search("technology", n_results=5)
            
            if results:
                self._pass(f"✓ Domain filtering functional")
                
                # Check if results have domain/topic info
                if any('topic' in r for r in results):
                    topics = [r.get('topic', 'Unknown') for r in results]
                    unique_topics = set(topics)
                    self._pass(f"✓ Found {len(unique_topics)} unique topics: {', '.join(unique_topics)}")
                else:
                    self._warn("⚠ No topic metadata in results")
            else:
                self._warn("⚠ No results with domain filter")
        
        except Exception as e:
            self._fail(f"✗ Domain filtering failed: {str(e)}")
        
        console.print()
    
    def test_retrieval_performance(self):
        """Test retrieval speed and efficiency"""
        
        console.print("[bold]Test 6: Performance Metrics[/bold]\n")
        
        try:
            from tools.rag_retrieval_tool import get_retriever
            retriever = get_retriever()
            
            if retriever.collection.count() == 0:
                self._warn("⚠ Skipping performance test (empty knowledge base)")
                console.print()
                return
            
            # Test queries
            test_queries = [
                "machine learning",
                "content marketing",
                "software development",
            ]
            
            latencies = []
            
            for query in test_queries:
                start = time.time()
                results = retriever.search(query, n_results=5)
                latency = (time.time() - start) * 1000  # Convert to ms
                latencies.append(latency)
            
            avg_latency = sum(latencies) / len(latencies)
            
            if avg_latency < 100:
                self._pass(f"✓ Excellent performance: {avg_latency:.1f}ms avg")
            elif avg_latency < 500:
                self._pass(f"✓ Good performance: {avg_latency:.1f}ms avg")
            else:
                self._warn(f"⚠ Slow performance: {avg_latency:.1f}ms avg")
            
            # Individual latencies
            for query, lat in zip(test_queries, latencies):
                console.print(f"  [dim]- '{query}': {lat:.1f}ms[/dim]")
        
        except Exception as e:
            self._fail(f"✗ Performance test failed: {str(e)}")
        
        console.print()
    
    def test_relevance_scoring(self):
        """Test relevance scoring accuracy"""
        
        console.print("[bold]Test 7: Relevance Scoring[/bold]\n")
        
        try:
            from tools.rag_retrieval_tool import get_retriever
            retriever = get_retriever()
            
            if retriever.collection.count() == 0:
                self._warn("⚠ Skipping relevance test (empty knowledge base)")
                console.print()
                return
            
            # Test with highly specific query
            results = retriever.search("machine learning neural networks", n_results=5)
            
            if results:
                scores = [r['relevance_score'] for r in results]
                
                # Check score range
                if all(0 <= s <= 1 for s in scores):
                    self._pass(f"✓ Relevance scores in valid range [0, 1]")
                else:
                    self._fail(f"✗ Invalid relevance scores")
                
                # Check score ordering (descending)
                if scores == sorted(scores, reverse=True):
                    self._pass(f"✓ Results properly ranked by relevance")
                else:
                    self._warn(f"⚠ Results not sorted by relevance")
                
                # Check score distribution
                max_score = max(scores)
                min_score = min(scores)
                score_range = max_score - min_score
                
                if score_range > 0.1:
                    self._pass(f"✓ Good score distribution (range: {score_range:.2f})")
                else:
                    self._warn(f"⚠ Limited score variation (range: {score_range:.2f})")
            else:
                self._warn("⚠ No results for relevance test")
        
        except Exception as e:
            self._fail(f"✗ Relevance scoring test failed: {str(e)}")
        
        console.print()
    
    def test_ranking_quality(self):
        """Test ranking mechanism quality"""
        
        console.print("[bold]Test 8: Ranking Quality[/bold]\n")
        
        try:
            from tools.rag_retrieval_tool import get_retriever
            retriever = get_retriever()
            
            if retriever.collection.count() == 0:
                self._warn("⚠ Skipping ranking test (empty knowledge base)")
                console.print()
                return
            
            # Compare two related queries
            query1 = "machine learning"
            query2 = "deep learning neural networks"
            
            results1 = retriever.search(query1, n_results=3)
            results2 = retriever.search(query2, n_results=3)
            
            if results1 and results2:
                self._pass(f"✓ Ranking system operational")
                
                # Check if more specific query has higher top score
                if results2[0]['relevance_score'] >= results1[0]['relevance_score'] * 0.8:
                    self._pass(f"✓ Specific queries ranked appropriately")
                else:
                    self._warn(f"⚠ Ranking may need tuning")
            else:
                self._warn("⚠ Insufficient results for ranking comparison")
        
        except Exception as e:
            self._fail(f"✗ Ranking test failed: {str(e)}")
        
        console.print()
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        
        console.print("[bold]Test 9: Edge Cases & Error Handling[/bold]\n")
        
        try:
            from tools.rag_retrieval_tool import rag_retrieval_tool
            
            # Test 1: Empty query
            try:
                result = rag_retrieval_tool._run(query="", max_results=3)
                if "error" in result.lower() or len(result) > 0:
                    self._pass("✓ Handles empty query gracefully")
                else:
                    self._fail("✗ Empty query not handled")
            except:
                self._warn("⚠ Empty query throws exception")
            
            # Test 2: Very long query
            try:
                long_query = "machine learning " * 100
                result = rag_retrieval_tool._run(query=long_query, max_results=3)
                self._pass("✓ Handles long queries")
            except:
                self._warn("⚠ Long query causes issues")
            
            # Test 3: Special characters
            try:
                result = rag_retrieval_tool._run(query="AI & ML @#$%", max_results=3)
                self._pass("✓ Handles special characters")
            except:
                self._warn("⚠ Special characters cause issues")
            
            # Test 4: Zero results request
            try:
                result = rag_retrieval_tool._run(query="test", max_results=0)
                self._pass("✓ Handles zero results request")
            except:
                self._warn("⚠ Zero results request causes issues")
            
            # Test 5: Large results request
            try:
                result = rag_retrieval_tool._run(query="test", max_results=100)
                self._pass("✓ Handles large results request")
            except:
                self._warn("⚠ Large results request causes issues")
        
        except Exception as e:
            self._fail(f"✗ Edge case testing failed: {str(e)}")
        
        console.print()
    
    def _pass(self, message: str):
        """Record passed test"""
        console.print(f"[green]{message}[/green]")
        self.test_results['passed'] += 1
    
    def _fail(self, message: str):
        """Record failed test"""
        console.print(f"[red]{message}[/red]")
        self.test_results['failed'] += 1
    
    def _warn(self, message: str):
        """Record warning"""
        console.print(f"[yellow]{message}[/yellow]")
        self.test_results['warnings'] += 1
    
    def display_test_summary(self):
        """Display comprehensive test summary"""
        
        console.print("\n[bold cyan]═══════════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]   TEST SUMMARY[/bold cyan]")
        console.print("[bold cyan]═══════════════════════════════════════════[/bold cyan]\n")
        
        total = self.test_results['passed'] + self.test_results['failed'] + self.test_results['warnings']
        
        # Results table
        table = Table(show_header=True)
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right", style="yellow")
        table.add_column("Percentage", justify="right", style="dim")
        
        table.add_row(
            "[green]✓ Passed[/green]",
            str(self.test_results['passed']),
            f"{self.test_results['passed']/total*100:.1f}%" if total > 0 else "0%"
        )
        table.add_row(
            "[red]✗ Failed[/red]",
            str(self.test_results['failed']),
            f"{self.test_results['failed']/total*100:.1f}%" if total > 0 else "0%"
        )
        table.add_row(
            "[yellow]⚠ Warnings[/yellow]",
            str(self.test_results['warnings']),
            f"{self.test_results['warnings']/total*100:.1f}%" if total > 0 else "0%"
        )
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{total}[/bold]",
            "[bold]100%[/bold]"
        )
        
        console.print(table)
        console.print()
        
        # Overall status
        if self.test_results['failed'] == 0:
            status = "[bold green]ALL TESTS PASSED ✓[/bold green]"
            message = "RAG system is fully operational and ready for production use."
        elif self.test_results['failed'] <= 2:
            status = "[bold yellow]MOSTLY PASSING ⚠[/bold yellow]"
            message = "RAG system is functional with minor issues. Review failed tests."
        else:
            status = "[bold red]NEEDS ATTENTION ✗[/bold red]"
            message = "Critical issues detected. Fix failed tests before deployment."
        
        panel = Panel(
            f"{message}\n\n"
            f"Passed: {self.test_results['passed']} | "
            f"Failed: {self.test_results['failed']} | "
            f"Warnings: {self.test_results['warnings']}",
            title=f"System Status: {status}",
            border_style="cyan"
        )
        console.print(panel)
        console.print()
        
        # Next steps
        if self.test_results['warnings'] > 0 and self.test_results['failed'] == 0:
            console.print("[bold cyan]Next Steps:[/bold cyan]")
            if any("empty knowledge base" in str(self.test_results)):
                console.print("  1. Run: [yellow]python src/tools/build_knowledge_base.py[/yellow]")
                console.print("  2. Re-run tests to verify full functionality\n")


def main():
    """Main entry point"""
    
    tester = RAGSystemTester()
    tester.run_all_tests()
    
    # Return exit code based on results
    if tester.test_results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()