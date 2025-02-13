from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import json
import pickle
from pathlib import Path
from datetime import datetime

class KnowledgeService:
    def __init__(self):
        self.base_path = Path("knowledge_base")
        self.base_path.mkdir(exist_ok=True)
        
        # Initialize FAISS index
        self.index_path = self.base_path / "vector_index.faiss"
        self.metadata_path = self.base_path / "metadata.json"
        self.embeddings_path = self.base_path / "embeddings.pkl"
        
        # Load sentence transformer model
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Initialize or load index
        self._initialize_index()

    def _initialize_index(self) -> None:
        """Initialize or load FAISS index and metadata"""
        if self.index_path.exists() and self.metadata_path.exists():
            # Load existing index
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            with open(self.embeddings_path, 'rb') as f:
                self.stored_embeddings = pickle.load(f)
        else:
            # Create new index
            embedding_size = self.model.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(embedding_size)
            self.metadata = {}
            self.stored_embeddings = {}

    def _save_index(self) -> None:
        """Save index and metadata to disk"""
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        with open(self.embeddings_path, 'wb') as f:
            pickle.dump(self.stored_embeddings, f)

    async def add_knowledge(self, 
                          content: str,
                          source: str,
                          doc_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add new knowledge to the base"""
        # Generate embedding
        embedding = self.model.encode([content])[0]
        
        # Generate ID if not provided
        if not doc_id:
            doc_id = f"k_{datetime.now().isoformat()}_{len(self.metadata)}"
        
        # Store metadata
        self.metadata[doc_id] = {
            "content": content,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to index
        self.index.add(np.array([embedding]))
        self.stored_embeddings[doc_id] = embedding
        
        # Save to disk
        self._save_index()
        
        return doc_id

    async def search_knowledge(self, 
                             query: str,
                             k: int = 5,
                             threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search knowledge base for similar content"""
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search index
        distances, indices = self.index.search(np.array([query_embedding]), k)
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # Valid index
                # Convert distance to similarity score (0-1)
                similarity = 1 - (distance / 2)  # Normalize distance
                
                if similarity >= threshold:
                    # Find corresponding doc_id
                    doc_id = list(self.stored_embeddings.keys())[idx]
                    
                    # Get metadata
                    metadata = self.metadata[doc_id]
                    results.append({
                        "id": doc_id,
                        "content": metadata["content"],
                        "source": metadata["source"],
                        "similarity": similarity,
                        "metadata": metadata["metadata"]
                    })
        
        return results

    async def get_knowledge(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific knowledge entry"""
        if doc_id in self.metadata:
            return {
                "id": doc_id,
                **self.metadata[doc_id]
            }
        return None

    async def update_knowledge(self,
                             doc_id: str,
                             content: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update existing knowledge entry"""
        if doc_id not in self.metadata:
            return False
        
        # Update content if provided
        if content is not None:
            # Generate new embedding
            new_embedding = self.model.encode([content])[0]
            
            # Find index of old embedding
            old_idx = list(self.stored_embeddings.keys()).index(doc_id)
            
            # Remove old embedding and add new one
            self.index.remove_ids(np.array([old_idx]))
            self.index.add(np.array([new_embedding]))
            
            # Update stored embeddings
            self.stored_embeddings[doc_id] = new_embedding
            
            # Update content in metadata
            self.metadata[doc_id]["content"] = content
        
        # Update metadata if provided
        if metadata is not None:
            self.metadata[doc_id]["metadata"].update(metadata)
        
        # Update timestamp
        self.metadata[doc_id]["timestamp"] = datetime.now().isoformat()
        
        # Save changes
        self._save_index()
        
        return True

    async def delete_knowledge(self, doc_id: str) -> bool:
        """Delete knowledge entry"""
        if doc_id not in self.metadata:
            return False
        
        # Find index of embedding to remove
        idx = list(self.stored_embeddings.keys()).index(doc_id)
        
        # Remove from index
        self.index.remove_ids(np.array([idx]))
        
        # Remove from stored data
        del self.stored_embeddings[doc_id]
        del self.metadata[doc_id]
        
        # Save changes
        self._save_index()
        
        return True

    async def get_related_knowledge(self, doc_id: str, k: int = 5) -> List[Dict[str, Any]]:
        """Find related knowledge entries"""
        if doc_id not in self.metadata:
            return []
        
        # Get embedding for the document
        embedding = self.stored_embeddings[doc_id]
        
        # Search for similar embeddings
        distances, indices = self.index.search(np.array([embedding]), k + 1)  # +1 because it will find itself
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1:  # Valid index
                # Find corresponding related_doc_id
                related_doc_id = list(self.stored_embeddings.keys())[idx]
                
                # Skip if it's the same document
                if related_doc_id == doc_id:
                    continue
                
                # Convert distance to similarity score
                similarity = 1 - (distance / 2)
                
                # Get metadata
                metadata = self.metadata[related_doc_id]
                results.append({
                    "id": related_doc_id,
                    "content": metadata["content"],
                    "source": metadata["source"],
                    "similarity": similarity,
                    "metadata": metadata["metadata"]
                })
        
        return results
