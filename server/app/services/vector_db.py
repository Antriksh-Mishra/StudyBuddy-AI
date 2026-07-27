import os
import pickle
import numpy as np
import faiss
from app.config import settings

class VectorDBService:
    def __init__(self, index_dir="vector_store"):
        self.index_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), index_dir)
        os.makedirs(self.index_dir, exist_ok=True)
        
        self.index_path = os.path.join(self.index_dir, "faiss_index.bin")
        self.meta_path = os.path.join(self.index_dir, "metadata.pkl")
        self.dimension = 768  # Default dimension for Gemini embedding-001 / text-embedding-004
        
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.meta_path, "rb") as f:
                    self.metadata = pickle.load(f)
                self.dimension = self.index.d
                print(f"[*] Loaded FAISS index with {self.index.ntotal} vectors of dimension {self.dimension}")
            except Exception as e:
                print(f"[*] Error loading vector store: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (Cosine similarity if normalized)
        self.metadata = []
        self._save()

    def _save(self):
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.meta_path, "wb") as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            print(f"[*] Failed to save FAISS index: {e}")

    def add_vectors(self, vectors: list, metadata_list: list):
        """
        Adds vectors (embeddings) and associated metadata list to the vector db.
        """
        if not vectors:
            return
        
        vectors_np = np.array(vectors).astype("float32")
        
        # Adjust dimensions if necessary
        dim = vectors_np.shape[1]
        if dim != self.dimension:
            print(f"[*] Re-initializing FAISS index due to dimension change: {self.dimension} -> {dim}")
            self.dimension = dim
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []
            
        # Normalize vectors for Cosine Similarity (Inner Product on normalized vectors)
        norms = np.linalg.norm(vectors_np, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1.0
        vectors_np = vectors_np / norms

        self.index.add(vectors_np)
        self.metadata.extend(metadata_list)
        self._save()

    def search_similar(self, query_vector: list, k: int = 4) -> list:
        """
        Searches for the k most similar chunks to the query vector.
        """
        if self.index.ntotal == 0:
            return []

        query_np = np.array([query_vector]).astype("float32")
        
        # Normalize query vector
        norm = np.linalg.norm(query_np)
        if norm > 0:
            query_np = query_np / norm

        distances, indices = self.index.search(query_np, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append({
                    "metadata": self.metadata[idx],
                    "score": float(distances[0][i])
                })
        return results

    def delete_document_vectors(self, document_id: int):
        """
        Removes all vectors belonging to a specific document ID.
        FAISS doesn't support easy deletes in IndexFlatIP without rebuilding,
        so we filter the metadata and rebuild the index.
        """
        if self.index.ntotal == 0:
            return

        # Extract remaining vectors and metadata
        remaining_meta = []
        remaining_vectors = []
        
        for i in range(self.index.ntotal):
            meta = self.metadata[i]
            if meta.get("document_id") != document_id:
                remaining_meta.append(meta)
                # Re-extract vector from index
                vector = self.index.reconstruct(i)
                remaining_vectors.append(vector)
        
        # Re-build index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        
        if remaining_vectors:
            self.add_vectors(remaining_vectors, remaining_meta)
        else:
            self._save()

vector_db = VectorDBService()
