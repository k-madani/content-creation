"""
RAG Retrieval Tool - Using only sentence-transformers + pickle
No ChromaDB dependency - pure Python implementation
"""

from crewai.tools import tool
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import pickle
import json
from typing import List, Dict
from collections import defaultdict
from utils.query_router import get_query_router


class SimpleRAGRetriever:
    """
    Simple but effective RAG using sentence-transformers + numpy
    No external vector DB needed
    """
    
    def __init__(self):
        self.kb_dir = Path("knowledge_base")
        self.kb_dir.mkdir(exist_ok=True)
        
        # Paths
        self.embeddings_path = self.kb_dir / "embeddings.npy"
        self.metadata_path = self.kb_dir / "metadata.pkl"
        
        # Load embedding model
        print("Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Model loaded")
        
        # Load existing data
        if self.embeddings_path.exists() and self.metadata_path.exists():
            self.embeddings = np.load(str(self.embeddings_path))
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"✓ Loaded {len(self.metadata)} chunks from knowledge base")
        else:
            self.embeddings = np.array([])
            self.metadata = []
            print("✓ Created new empty index")
    
    def search(self, query: str, n_results: int = 5, min_relevance: float = 0.3) -> List[Dict]:
        """
        Semantic search using cosine similarity
        """
        
        if len(self.metadata) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedder.encode([query])[0]
        
        # Compute cosine similarities
        similarities = self._cosine_similarity(query_embedding, self.embeddings)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:n_results * 2]  # Get more for filtering
        
        # Format results
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
            
            # Keyword boost
            query_terms = set(query.lower().split())
            content = result.get('content', '').lower()
            keyword_matches = sum(1 for term in query_terms if term in content)
            keyword_score = min(0.2, keyword_matches * 0.05)
            
            result['keyword_score'] = keyword_score
            result['relevance_score'] = min(1.0, similarity + keyword_score)
            
            results.append(result)
        
        # Sort by final relevance
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:n_results]
    
    def _cosine_similarity(self, query_emb: np.ndarray, doc_embs: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and documents"""
        
        # Normalize
        query_norm = query_emb / np.linalg.norm(query_emb)
        doc_norms = doc_embs / np.linalg.norm(doc_embs, axis=1, keepdims=True)
        
        # Compute dot product (cosine similarity)
        similarities = np.dot(doc_norms, query_norm)
        
        return similarities
    
    def add_documents(self, chunks: List[Dict]):
        """Add new documents to the knowledge base"""
        
        if not chunks:
            return
        
        # Generate embeddings
        texts = [c['text'] for c in chunks]
        new_embeddings = self.embedder.encode(texts, show_progress_bar=True)
        
        # Append to existing
        if len(self.embeddings) == 0:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
        
        # Add metadata
        for chunk in chunks:
            meta = {
                'content': chunk['text'],
                'source': chunk.get('source', 'Unknown'),
                'topic': chunk.get('topic', 'General'),
                'chunk_id': chunk.get('chunk_id', len(self.metadata)),
                'word_count': len(chunk['text'].split())
            }
            self.metadata.append(meta)
        
        # Save
        self._save()
    
    def _save(self):
        """Save embeddings and metadata"""
        np.save(str(self.embeddings_path), self.embeddings)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def get_collection_stats(self) -> Dict:
        """Get knowledge base statistics"""
        
        stats = {
            'total_chunks': len(self.metadata),
            'status': 'available' if len(self.metadata) > 0 else 'empty'
        }
        
        if self.metadata:
            # Domain distribution
            domains = defaultdict(int)
            for meta in self.metadata:
                domains[meta.get('topic', 'Unknown')] += 1
            stats['domains'] = dict(domains)
        
        return stats


# Global retriever instance
_retriever = None

def get_retriever():
    """Get or create retriever singleton"""
    global _retriever
    if _retriever is None:
        _retriever = SimpleRAGRetriever()
    return _retriever


@tool("RAG Knowledge Base Search")
def rag_retrieval_tool(query: str, max_results: int = 5) -> str:
    """
    Search the local knowledge base using semantic similarity.
    Retrieves relevant information from previously ingested documents.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        Formatted search results with sources and relevance scores
    """
    
    try:
        router = get_query_router()
        routing = router.analyze_query(query)
        retriever = get_retriever()
        stats = retriever.get_collection_stats()
        
        if stats['total_chunks'] == 0:
            return (
                "⚠️ Knowledge Base Empty\n\n"
                "The RAG knowledge base has no documents yet.\n"
                "Run: python src/utils/build_knowledge_base.py\n"
                "to ingest documents into the knowledge base.\n\n"
                "Falling back to web search..."
            )
        
        # Perform search
        results = retriever.search(query, max_results, min_relevance=0.3)
        
        # Record result for router learning
        router.record_rag_result(routing['domain'], len(results) > 0)
        
        if not results:
            return (
                f"# RAG Search Results for: {query}\n\n"
                f"⚠️ No relevant results found in knowledge base ({stats['total_chunks']} chunks available)\n"
                f"Try refining your query or falling back to web search.\n"
            )
        
        # Format results
        formatted = f"# RAG Knowledge Base Results\n\n"
        formatted += f"**Query:** {query}\n"
        formatted += f"**Knowledge Base:** {stats['total_chunks']} chunks available\n"
        formatted += f"**Retrieved:** {len(results)} relevant results\n"
        formatted += f"**Search Method:** Semantic (Cosine Similarity)\n\n"
        formatted += "---\n\n"
        
        for i, result in enumerate(results, 1):
            relevance = result['relevance_score'] * 100
            
            # Relevance indicator
            if relevance >= 70:
                indicator = "🟢 HIGHLY RELEVANT"
            elif relevance >= 50:
                indicator = "🟡 RELEVANT"
            else:
                indicator = "🟠 SOMEWHAT RELEVANT"
            
            formatted += f"## Result {i}: {indicator} ({relevance:.1f}%)\n\n"
            formatted += f"**Source:** {result.get('source', 'Unknown')}\n"
            formatted += f"**Topic:** {result.get('topic', 'General')}\n"
            formatted += f"**Chunk:** {result.get('chunk_id', 0) + 1}\n"
            formatted += f"**Scores:** Semantic: {result.get('semantic_score', 0):.2f} | "
            formatted += f"Keyword: {result.get('keyword_score', 0):.2f}\n\n"
            formatted += f"**Content:**\n{result.get('content', '')}\n\n"
            formatted += "---\n\n"
        
        return formatted
        
    except Exception as e:
        return (
            f"# RAG Search Error\n\n"
            f"Error: {str(e)}\n\n"
            f"Falling back to web search..."
        )