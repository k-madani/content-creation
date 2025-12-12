"""
Query Router - Intelligent RAG Usage
Determines if RAG will be helpful before calling it
"""

from typing import Dict, List, Tuple
from rich.console import Console

console = Console()


class QueryRouter:
    """
    Routes queries to appropriate search strategy
    
    Features:
    - Domain classification
    - RAG relevance prediction
    - Search strategy optimization
    - Performance tracking
    """
    
    def __init__(self):
        # Domain keywords (matches your knowledge base)
        self.domain_keywords = {
            'ai_ml': [
                'machine learning', 'artificial intelligence', 'deep learning',
                'neural network', 'ai', 'ml', 'algorithm', 'model training',
                'data science', 'nlp', 'computer vision', 'reinforcement learning'
            ],
            'technology': [
                'software', 'programming', 'code', 'development', 'algorithm',
                'tech', 'computer', 'system', 'application', 'framework',
                'api', 'database', 'architecture', 'devops', 'cloud'
            ],
            'business': [
                'business', 'marketing', 'sales', 'strategy', 'growth',
                'revenue', 'roi', 'customer', 'market', 'brand',
                'advertising', 'campaign', 'seo', 'content marketing'
            ],
            'software_dev': [
                'agile', 'scrum', 'testing', 'deployment', 'ci/cd',
                'git', 'version control', 'clean code', 'design pattern',
                'microservices', 'docker', 'kubernetes'
            ]
        }
        
        # Performance tracking
        self.stats = {
            'total_queries': 0,
            'rag_recommended': 0,
            'rag_skipped': 0,
            'rag_hits': 0,
            'rag_misses': 0,
            'web_only': 0
        }
        
        # Domain hit rates (updated after searches)
        self.domain_hit_rates = {
            'ai_ml': 0.9,  # 90% of AI/ML queries have RAG results
            'technology': 0.75,
            'business': 0.70,
            'software_dev': 0.80,
            'unknown': 0.1  # Low hit rate for unknown domains
        }
    
    def analyze_query(self, query: str) -> Dict:
        """
        Analyze query and determine search strategy
        
        Args:
            query: User's search query
            
        Returns:
            Dict with domain, confidence, and recommendation
        """
        
        self.stats['total_queries'] += 1
        
        query_lower = query.lower()
        
        # Classify domain
        domain, confidence = self._classify_domain(query_lower)
        
        # Predict RAG usefulness
        should_use_rag = self._should_use_rag(domain, confidence, query_lower)
        
        # Get search strategy
        strategy = self._get_search_strategy(should_use_rag, domain)
        
        return {
            'domain': domain,
            'confidence': confidence,
            'use_rag': should_use_rag,
            'strategy': strategy,
            'expected_hit_rate': self.domain_hit_rates.get(domain, 0.1)
        }
    
    def _classify_domain(self, query: str) -> Tuple[str, float]:
        """
        Classify query into domain
        
        Returns:
            (domain_name, confidence_score)
        """
        
        domain_scores = {}
        
        # Score each domain
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                domain_scores[domain] = score
        
        if not domain_scores:
            return 'unknown', 0.0
        
        # Get best domain
        best_domain = max(domain_scores, key=domain_scores.get)
        max_score = domain_scores[best_domain]
        
        # Calculate confidence (normalized by keyword count)
        confidence = min(1.0, max_score / 3)  # 3+ matches = high confidence
        
        return best_domain, confidence
    
    def _should_use_rag(self, domain: str, confidence: float, query: str) -> bool:
        """
        Determine if RAG should be used
        
        Decision factors:
        1. Domain match confidence
        2. Domain historical hit rate
        3. Query characteristics
        """
        
        # Skip RAG if very low confidence in domain
        if confidence < 0.2:
            return False
        
        # Skip RAG if domain has low hit rate
        expected_hit_rate = self.domain_hit_rates.get(domain, 0.1)
        if expected_hit_rate < 0.3:
            return False
        
        # Skip RAG for very specific/current queries
        current_indicators = ['2024', '2025', 'latest', 'recent', 'news', 'today']
        if any(indicator in query for indicator in current_indicators):
            # Current events likely not in KB
            if confidence < 0.7:  # Unless very confident in domain
                return False
        
        # Skip RAG for location-specific queries (unless tech/business)
        location_indicators = ['nyc', 'new york', 'city', 'travel', 'visit', 'restaurant']
        if any(indicator in query for indicator in location_indicators):
            if domain not in ['technology', 'business', 'ai_ml']:
                return False
        
        return True
    
    def _get_search_strategy(self, use_rag: bool, domain: str) -> str:
        """
        Determine optimal search strategy
        
        Returns:
            'rag_primary': Try RAG first, web fallback
            'rag_hybrid': Use both RAG and web in parallel
            'web_only': Skip RAG, use web directly
        """
        
        if not use_rag:
            self.stats['web_only'] += 1
            return 'web_only'
        
        # High-confidence domains: try RAG first
        if domain in ['ai_ml', 'software_dev'] and self.domain_hit_rates[domain] > 0.75:
            self.stats['rag_recommended'] += 1
            return 'rag_primary'
        
        # Medium-confidence: hybrid approach
        if domain in ['technology', 'business']:
            self.stats['rag_recommended'] += 1
            return 'rag_hybrid'
        
        self.stats['rag_recommended'] += 1
        return 'rag_primary'
    
    def record_rag_result(self, domain: str, found_results: bool):
        """
        Record RAG search result to improve future routing
        
        Args:
            domain: Domain that was searched
            found_results: Whether RAG returned useful results
        """
        
        if found_results:
            self.stats['rag_hits'] += 1
            # Slightly increase hit rate for this domain
            if domain in self.domain_hit_rates:
                current_rate = self.domain_hit_rates[domain]
                self.domain_hit_rates[domain] = min(0.95, current_rate * 1.05)
        else:
            self.stats['rag_misses'] += 1
            # Slightly decrease hit rate for this domain
            if domain in self.domain_hit_rates:
                current_rate = self.domain_hit_rates[domain]
                self.domain_hit_rates[domain] = max(0.05, current_rate * 0.95)
    
    def get_statistics(self) -> Dict:
        """Get routing statistics"""
        
        total = self.stats['total_queries']
        if total == 0:
            return self.stats
        
        rag_total = self.stats['rag_hits'] + self.stats['rag_misses']
        rag_accuracy = self.stats['rag_hits'] / rag_total if rag_total > 0 else 0
        
        return {
            **self.stats,
            'rag_accuracy': rag_accuracy,
            'rag_usage_rate': self.stats['rag_recommended'] / total,
            'web_only_rate': self.stats['web_only'] / total,
            'domain_hit_rates': self.domain_hit_rates
        }
    
    def display_statistics(self):
        """Display routing statistics"""
        from rich.table import Table
        
        stats = self.get_statistics()
        
        console.print("\n[bold cyan]Query Router Statistics:[/bold cyan]\n")
        
        # Overall stats
        table = Table(show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="yellow")
        
        table.add_row("Total Queries", str(stats['total_queries']))
        table.add_row("RAG Recommended", str(stats['rag_recommended']))
        table.add_row("Web Only", str(stats['web_only']))
        table.add_row("RAG Hit Rate", f"{stats.get('rag_accuracy', 0):.1%}")
        
        console.print(table)
        
        # Domain hit rates
        console.print("\n[bold cyan]Domain Hit Rates:[/bold cyan]")
        domain_table = Table(show_header=False)
        domain_table.add_column("Domain", style="cyan")
        domain_table.add_column("Hit Rate", justify="right", style="yellow")
        
        for domain, rate in stats.get('domain_hit_rates', {}).items():
            if domain != 'unknown':
                domain_table.add_row(domain.replace('_', ' ').title(), f"{rate:.1%}")
        
        console.print(domain_table)
        console.print()


# Global singleton
_query_router = None

def get_query_router() -> QueryRouter:
    """Get or create query router singleton"""
    global _query_router
    if _query_router is None:
        _query_router = QueryRouter()
    return _query_router