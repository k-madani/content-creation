"""
RAG Retrieval Tool - No ChromaDB dependency
Uses sentence-transformers + NumPy only
"""

from crewai.tools import tool
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import pickle
from typing import List, Dict
from collections import defaultdict


class SimpleRAGRetriever:
    """Simple but effective RAG using sentence-transformers + numpy"""
    
    def __init__(self):
        self.kb_dir = Path("knowledge_base")
        self.kb_dir.mkdir(exist_ok=True)
        
        self.embeddings_path = self.kb_dir / "embeddings.npy"
        self.metadata_path = self.kb_dir / "metadata.pkl"
        
        print("Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Model loaded")
        
        if self.embeddings_path.exists() and self.metadata_path.exists():
            self.embeddings = np.load(str(self.embeddings_path))
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"✓ Loaded {len(self.metadata)} chunks")
        else:
            self.embeddings = np.array([])
            self.metadata = []
            print("✓ Created new empty index")
    
    def search(self, query: str, n_results: int = 5, min_relevance: float = 0.3) -> List[Dict]:
        """Semantic search using cosine similarity"""
        
        if len(self.metadata) == 0:
            return []
        
        query_embedding = self.embedder.encode([query])[0]
        similarities = self._cosine_similarity(query_embedding, self.embeddings)
        top_indices = np.argsort(similarities)[::-1][:n_results * 2]
        
        results = []
        for idx in top_indices:
            if idx >= len(self.metadata):
                continue
            
            similarity = float(similarities[idx])
            if similarity < min_relevance:
                continue
            
            result = self.metadata[idx].copy()
            result['relevance_score'] = similarity
            result['semantic_score'] = similarity
            
            query_terms = set(query.lower().split())
            content = result.get('content', '').lower()
            keyword_matches = sum(1 for term in query_terms if term in content)
            keyword_score = min(0.2, keyword_matches * 0.05)
            
            result['keyword_score'] = keyword_score
            result['relevance_score'] = min(1.0, similarity + keyword_score)
            results.append(result)
        
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:n_results]
    
    def _cosine_similarity(self, query_emb: np.ndarray, doc_embs: np.ndarray) -> np.ndarray:
        """Compute cosine similarity"""
        query_norm = query_emb / np.linalg.norm(query_emb)
        doc_norms = doc_embs / np.linalg.norm(doc_embs, axis=1, keepdims=True)
        return np.dot(doc_norms, query_norm)
    
    def get_collection_stats(self) -> Dict:
        """Get statistics"""
        stats = {
            'total_chunks': len(self.metadata),
            'status': 'available' if len(self.metadata) > 0 else 'empty'
        }
        
        if self.metadata:
            domains = defaultdict(int)
            for meta in self.metadata:
                domains[meta.get('topic', 'Unknown')] += 1
            stats['domains'] = dict(domains)
        
        return stats


_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = SimpleRAGRetriever()
    return _retriever


@tool("RAG Knowledge Base Search")
def rag_retrieval_tool(query: str, max_results: int = 5) -> str:
    """Search knowledge base using semantic similarity"""
    
    try:
        retriever = get_retriever()
        stats = retriever.get_collection_stats()
        
        if stats['total_chunks'] == 0:
            return (
                "⚠️ Knowledge Base Empty\n\n"
                "Run: python src/tools/build_knowledge_base.py\n"
                "Falling back to web search..."
            )
        
        results = retriever.search(query, max_results, min_relevance=0.3)
        
        if not results:
            return f"# RAG: No relevant results\nFalling back to web search..."
        
        formatted = f"# RAG Results\n\nQuery: {query}\nFound: {len(results)} results\n\n---\n\n"
        
        for i, result in enumerate(results, 1):
            relevance = result['relevance_score'] * 100
            indicator = "🟢" if relevance >= 70 else "🟡" if relevance >= 50 else "🟠"
            
            formatted += f"## Result {i}: {indicator} ({relevance:.1f}%)\n\n"
            formatted += f"**Source:** {result['source']}\n"
            formatted += f"**Topic:** {result['topic']}\n\n"
            formatted += f"**Content:**\n{result['content']}\n\n---\n\n"
        
        return formatted
        
    except Exception as e:
        return f"RAG Error: {str(e)}\nFalling back to web search..."