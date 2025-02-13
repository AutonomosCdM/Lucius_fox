import os
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import hashlib
from pathlib import Path

class DocumentService:
    def __init__(self):
        self.base_path = Path("research_documents")
        self.base_path.mkdir(exist_ok=True)
        self.index_file = self.base_path / "research_index.json"
        self.document_index = self._load_index()

    def _load_index(self) -> Dict[str, Any]:
        """Load the document index from file"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "documents": {},
            "topics": {},
            "tags": {}
        }

    def _save_index(self) -> None:
        """Save the document index to file"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.document_index, f, indent=2, ensure_ascii=False)

    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for a document"""
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"doc_{timestamp}_{content_hash}"

    async def save_research(self, research_data: Dict[str, Any]) -> str:
        """Save research data and return document ID"""
        # Generate unique ID
        doc_id = self._generate_id(str(research_data))
        
        # Create document metadata
        metadata = {
            "id": doc_id,
            "timestamp": datetime.now().isoformat(),
            "query": research_data.get('query', ''),
            "topics": [],  # Will be filled by analyze_and_tag
            "tags": [],    # Will be filled by analyze_and_tag
            "type": "research"
        }
        
        # Save document content
        doc_path = self.base_path / f"{doc_id}.json"
        document = {
            "metadata": metadata,
            "content": research_data
        }
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, indent=2, ensure_ascii=False)
        
        # Update index
        self.document_index["documents"][doc_id] = metadata
        self._save_index()
        
        return doc_id

    async def analyze_and_tag(self, doc_id: str, topics: List[str], tags: List[str]) -> None:
        """Add topics and tags to a document"""
        if doc_id not in self.document_index["documents"]:
            raise ValueError(f"Document {doc_id} not found")
        
        # Update document metadata
        self.document_index["documents"][doc_id]["topics"] = topics
        self.document_index["documents"][doc_id]["tags"] = tags
        
        # Update topics index
        for topic in topics:
            if topic not in self.document_index["topics"]:
                self.document_index["topics"][topic] = []
            if doc_id not in self.document_index["topics"][topic]:
                self.document_index["topics"][topic].append(doc_id)
        
        # Update tags index
        for tag in tags:
            if tag not in self.document_index["tags"]:
                self.document_index["tags"][tag] = []
            if doc_id not in self.document_index["tags"][tag]:
                self.document_index["tags"][tag].append(doc_id)
        
        self._save_index()

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by ID"""
        doc_path = self.base_path / f"{doc_id}.json"
        if not doc_path.exists():
            return None
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    async def search_documents(self, 
                             query: Optional[str] = None,
                             topics: Optional[List[str]] = None,
                             tags: Optional[List[str]] = None,
                             date_from: Optional[str] = None,
                             date_to: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search documents by various criteria"""
        results = []
        
        for doc_id, metadata in self.document_index["documents"].items():
            # Check if document matches all criteria
            matches = True
            
            # Check query
            if query and query.lower() not in metadata["query"].lower():
                matches = False
            
            # Check topics
            if topics and not all(topic in metadata["topics"] for topic in topics):
                matches = False
            
            # Check tags
            if tags and not all(tag in metadata["tags"] for tag in tags):
                matches = False
            
            # Check date range
            if date_from or date_to:
                doc_date = datetime.fromisoformat(metadata["timestamp"])
                if date_from and doc_date < datetime.fromisoformat(date_from):
                    matches = False
                if date_to and doc_date > datetime.fromisoformat(date_to):
                    matches = False
            
            if matches:
                document = await self.get_document(doc_id)
                if document:
                    results.append(document)
        
        return results

    async def get_related_documents(self, doc_id: str) -> List[Dict[str, Any]]:
        """Find documents related to a given document"""
        if doc_id not in self.document_index["documents"]:
            return []
        
        # Get document's topics and tags
        doc_metadata = self.document_index["documents"][doc_id]
        doc_topics = set(doc_metadata["topics"])
        doc_tags = set(doc_metadata["tags"])
        
        related_docs = []
        for other_id, other_metadata in self.document_index["documents"].items():
            if other_id == doc_id:
                continue
            
            # Calculate similarity based on shared topics and tags
            other_topics = set(other_metadata["topics"])
            other_tags = set(other_metadata["tags"])
            
            topic_similarity = len(doc_topics & other_topics) / len(doc_topics | other_topics) if doc_topics or other_topics else 0
            tag_similarity = len(doc_tags & other_tags) / len(doc_tags | other_tags) if doc_tags or other_tags else 0
            
            # Use weighted similarity
            similarity = (0.7 * topic_similarity) + (0.3 * tag_similarity)
            
            if similarity > 0.3:  # Threshold for relatedness
                document = await self.get_document(other_id)
                if document:
                    document["similarity"] = similarity
                    related_docs.append(document)
        
        # Sort by similarity
        related_docs.sort(key=lambda x: x["similarity"], reverse=True)
        return related_docs

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document and update indices"""
        if doc_id not in self.document_index["documents"]:
            return False
        
        # Remove file
        doc_path = self.base_path / f"{doc_id}.json"
        if doc_path.exists():
            doc_path.unlink()
        
        # Remove from topics index
        metadata = self.document_index["documents"][doc_id]
        for topic in metadata["topics"]:
            if topic in self.document_index["topics"]:
                self.document_index["topics"][topic].remove(doc_id)
                if not self.document_index["topics"][topic]:
                    del self.document_index["topics"][topic]
        
        # Remove from tags index
        for tag in metadata["tags"]:
            if tag in self.document_index["tags"]:
                self.document_index["tags"][tag].remove(doc_id)
                if not self.document_index["tags"][tag]:
                    del self.document_index["tags"][tag]
        
        # Remove from documents index
        del self.document_index["documents"][doc_id]
        
        self._save_index()
        return True
