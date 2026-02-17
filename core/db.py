import sqlite3
import datetime
import hashlib
from typing import List, Optional, Dict, Any
from tenacity import retry, stop_after_delay, wait_fixed, retry_if_exception_type

import chromadb
from chromadb.utils import embedding_functions

from core import config

class BrainDB:
    def __init__(self):
        # Ensure data directory exists
        config.BASE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=str(config.BASE_DATA_DIR))
        
        # Use default sentence-transformers model as specified in config
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=config.EMBEDDING_MODEL
        )
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    @retry(
        stop=stop_after_delay(config.DB_LOCK_RETRY_SECONDS),
        wait=wait_fixed(config.DB_LOCK_RETRY_INTERVAL),
        retry=retry_if_exception_type(sqlite3.OperationalError)
    )
    def add_memory(self, memory_id: str, text: str, metadata: Dict[str, Any]):
        """Add a new memory chunk with metadata."""
        # Ensure mandatory metadata fields
        metadata.setdefault("created_at", datetime.datetime.now(datetime.timezone.utc).isoformat())
        metadata.setdefault("schema_version", config.DB_SCHEMA_VERSION)
        
        self.collection.upsert(
            ids=[memory_id],
            documents=[text],
            metadatas=[metadata]
        )

    @retry(
        stop=stop_after_delay(config.DB_LOCK_RETRY_SECONDS),
        wait=wait_fixed(config.DB_LOCK_RETRY_INTERVAL),
        retry=retry_if_exception_type(sqlite3.OperationalError)
    )
    def update_memory(self, memory_id: str, new_text: str):
        """Update existing memory text."""
        self.collection.update(
            ids=[memory_id],
            documents=[new_text]
        )

    @retry(
        stop=stop_after_delay(config.DB_LOCK_RETRY_SECONDS),
        wait=wait_fixed(config.DB_LOCK_RETRY_INTERVAL),
        retry=retry_if_exception_type(sqlite3.OperationalError)
    )
    def delete_memory(self, memory_id: str):
        """Delete memory by ID."""
        self.collection.delete(ids=[memory_id])

    @retry(
        stop=stop_after_delay(config.DB_LOCK_RETRY_SECONDS),
        wait=wait_fixed(config.DB_LOCK_RETRY_INTERVAL),
        retry=retry_if_exception_type(sqlite3.OperationalError)
    )
    def search(self, query: str, workbase_id: str, limit: int = 5, category: Optional[str] = None) -> Dict[str, Any]:
        """Search memories using vector similarity, filtered by workbase."""
        where = {"workbase_id": workbase_id}
        if category:
            where["category"] = category
            
        return self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where
        )

    @retry(
        stop=stop_after_delay(config.DB_LOCK_RETRY_SECONDS),
        wait=wait_fixed(config.DB_LOCK_RETRY_INTERVAL),
        retry=retry_if_exception_type(sqlite3.OperationalError)
    )
    def check_conflict(self, text: str, workbase_id: str, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Check for semantic conflicts or duplicates.
        Returns the most similar conflicting rule if distance < CONFLICT_DISTANCE_THRESHOLD.
        If category is provided, it prioritizes findings within that category.
        """
        where_clauses = [
            {"workbase_id": workbase_id},
            {"type": "rule"}
        ]
        
        if category:
            where_clauses.append({"category": category})

        results = self.collection.query(
            query_texts=[text],
            n_results=1,
            where={"$and": where_clauses}
        )
        
        if results["ids"] and results["ids"][0]:
            distance = results["distances"][0][0]
            if distance < config.CONFLICT_DISTANCE_THRESHOLD:
                return {
                    "id": results["ids"][0][0],
                    "text": results["documents"][0][0],
                    "distance": distance,
                    "metadata": results["metadatas"][0][0]
                }
        return None

    @retry(
        stop=stop_after_delay(config.DB_LOCK_RETRY_SECONDS),
        wait=wait_fixed(config.DB_LOCK_RETRY_INTERVAL),
        retry=retry_if_exception_type(sqlite3.OperationalError)
    )
    def export_memory_to_json(self, workbase_id: Optional[str] = None) -> str:
        """Export memories (optionally filtered by workbase_id) to a JSON string."""
        import json
        if workbase_id:
            results = self.collection.get(where={"workbase_id": workbase_id})
        else:
            results = self.collection.get()
            
        export_data = []
        if results["ids"]:
            for i in range(len(results["ids"])):
                export_data.append({
                    "id": results["ids"][i],
                    "document": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
        return json.dumps(export_data, indent=2)

    @retry(
        stop=stop_after_delay(config.DB_LOCK_RETRY_SECONDS),
        wait=wait_fixed(config.DB_LOCK_RETRY_INTERVAL),
        retry=retry_if_exception_type(sqlite3.OperationalError)
    )
    def import_memory_from_json(self, json_data: str, target_workbase_id: Optional[str] = None, target_project_name: Optional[str] = None) -> int:
        """
        Import memories from a JSON string.
        If target_workbase_id is provided, all imported memories will be reassigned to this workbase.
        """
        import json
        data = json.loads(json_data)
        if not isinstance(data, list):
            raise ValueError("Invalid JSON format: expected a list of memories.")
        
        final_ids = []
        final_docs = []
        final_metadatas = []

        for item in data:
            doc = item["document"]
            meta = item["metadata"]
            
            if target_workbase_id:
                meta["workbase_id"] = target_workbase_id
                if target_project_name:
                    meta["project_name"] = target_project_name
                
                # Regenerate ID if it follows the pattern type_wb_hash to avoid cross-wb collisions or ghosting
                content_hash = hashlib.md5(doc.encode("utf-8")).hexdigest()
                m_type = meta.get("type", "context")
                item_id = f"{m_type}_{target_workbase_id}_{content_hash}"
            else:
                item_id = item["id"]

            final_ids.append(item_id)
            final_docs.append(doc)
            final_metadatas.append(meta)

        self.collection.upsert(
            ids=final_ids,
            documents=final_docs,
            metadatas=final_metadatas
        )
        return len(final_ids)

    @retry(
        stop=stop_after_delay(config.DB_LOCK_RETRY_SECONDS),
        wait=wait_fixed(config.DB_LOCK_RETRY_INTERVAL),
        retry=retry_if_exception_type(sqlite3.OperationalError)
    )
    def get_rules(self, workbase_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all rules for a specific workbase (or all if None)."""
        where = {"type": "rule"}
        if workbase_id:
            where = {"$and": [{"workbase_id": workbase_id}, {"type": "rule"}]}
            
        results = self.collection.get(where=where)
        
        memories = []
        for i in range(len(results["ids"])):
            memories.append({
                "id": results["ids"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i]
            })
        return memories
