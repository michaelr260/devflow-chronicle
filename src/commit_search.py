"""
Commit Search Engine - RAG Preview
Vector-based semantic search through commit history
"""

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
    VECTOR_SEARCH_AVAILABLE = True
except ImportError:
    VECTOR_SEARCH_AVAILABLE = False
    print("Warning: Vector search dependencies not installed")

from typing import List, Dict, Optional


class CommitSearchEngine:
    """
    Semantic search engine for commit history
    Preview of RAG concepts for Day 3!
    """

    def __init__(self):
        if not VECTOR_SEARCH_AVAILABLE:
            raise ImportError("Install sentence-transformers and faiss-cpu for vector search")

        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.commits = []
        self.embeddings = None

    def index_commits(self, commits: List[Dict]):
        """Create vector index of commits"""
        print("    Indexing commits for semantic search...")

        self.commits = commits
        messages = [c['message'] for c in commits]

        # Generate embeddings
        self.embeddings = self.model.encode(messages, show_progress_bar=False)

        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))

        print(f"   [OK] Indexed {len(commits)} commits")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Semantic search for similar commits

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of similar commits with similarity scores
        """
        if self.index is None:
            return []

        # Encode query
        query_embedding = self.model.encode([query])

        # Search
        distances, indices = self.index.search(
            query_embedding.astype('float32'),
            min(top_k, len(self.commits))
        )

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.commits):
                similarity = 1 / (1 + float(distance))
                results.append({
                    'commit': self.commits[idx],
                    'similarity': round(similarity, 3),
                    'distance': float(distance)
                })

        return results


if __name__ == "__main__":
    print("Commit Search Engine - RAG Preview")
