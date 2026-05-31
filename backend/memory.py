"""
Sierra Memory Module - Long-term Memory + RAG Foundation

Provides persistent, semantic memory across sessions.
Enables:
- Continuity of context and user preferences
- Self-improvement through reflection on past interactions
- Proactive suggestions based on history
- RAG-style retrieval for relevant past projects/notes

Backed by ChromaDB (vector store) + sentence-transformers (embeddings).
Designed to be safe, queryable, and integrable with the on-device router + Gemini.

Future: Integrate with project_manager, support reflection loops, and feed into multi-agent orchestrator.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    from sentence_transformers import SentenceTransformer
    MEMORY_DEPS_AVAILABLE = True
except ImportError:
    MEMORY_DEPS_AVAILABLE = False
    print("[MEMORY] chromadb or sentence-transformers not installed. Memory will run in degraded mode.")


class SierraMemory:
    def __init__(self, persist_directory: str = "long_term_memory/chroma", collection_name: str = "sierra_memory"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.embedder = None
        self.enabled = False

        if not MEMORY_DEPS_AVAILABLE:
            print("[MEMORY] Running in file-based fallback mode (no vector search).")
            self._init_fallback()
            return

        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            # Use a lightweight, fast embedding model
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            self.enabled = True
            print(f"[MEMORY] ChromaDB + embeddings initialized. Collection: {collection_name}")
        except Exception as e:
            print(f"[MEMORY] Failed to initialize vector memory: {e}. Falling back.")
            self._init_fallback()

    def _init_fallback(self):
        """Simple JSONL file-based memory when vector deps unavailable."""
        self.memory_file = self.persist_directory / "memory_fallback.jsonl"
        self.enabled = True  # Still usable for storage/retrieval

    def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None, source: str = "user") -> str:
        """Store a new memory entry. Returns entry ID."""
        if not self.enabled:
            return ""

        entry = {
            "id": f"mem_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "text": text,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        if self.collection is not None and self.embedder is not None:
            try:
                embedding = self.embedder.encode([text]).tolist()[0]
                self.collection.add(
                    documents=[text],
                    metadatas=[entry],
                    ids=[entry["id"]],
                    embeddings=[embedding]
                )
                return entry["id"]
            except Exception as e:
                print(f"[MEMORY] Vector add failed: {e}")

        # Fallback: append to JSONL
        try:
            with open(self.memory_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            return entry["id"]
        except Exception as e:
            print(f"[MEMORY] Fallback write failed: {e}")
            return ""

    def query_memory(self, query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """Semantic search for relevant memories. Returns list of entries."""
        if not self.enabled:
            return []

        if self.collection is not None and self.embedder is not None:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=filter_metadata
                )
                memories = []
                for i in range(len(results['ids'][0])):
                    memories.append({
                        "id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })
                return memories
            except Exception as e:
                print(f"[MEMORY] Vector query failed: {e}")

        # Fallback: simple keyword scan of JSONL
        results = []
        if hasattr(self, 'memory_file') and self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        if query.lower() in entry.get("text", "").lower():
                            results.append(entry)
                            if len(results) >= n_results:
                                break
            except Exception:
                pass
        return results

    def get_relevant_context(self, query: str, max_tokens: int = 2000) -> str:
        """Return concatenated relevant memories as context string for prompts."""
        memories = self.query_memory(query, n_results=6)
        if not memories:
            return ""
        context_parts = []
        for m in memories:
            text = m.get("text", "")
            ts = m.get("metadata", {}).get("timestamp", "")[:10]
            context_parts.append(f"[{ts}] {text}")
        return "\n".join(context_parts)[:max_tokens]

    def reflect_and_improve(self, recent_interaction: str) -> Optional[str]:
        """Simple self-improvement hook: analyze recent interaction and suggest improvements.
        Future: Use LLM to generate insights and store them."""
        # Placeholder for reflection loop
        if "error" in recent_interaction.lower() or "failed" in recent_interaction.lower():
            insight = f"User encountered an issue: {recent_interaction[:100]}... Consider improving error handling or adding confirmation."
            self.add_memory(insight, {"type": "reflection", "source": "system"})
            return insight
        return None


# Global instance for easy import
memory = SierraMemory()
