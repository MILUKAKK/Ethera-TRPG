"""Semantic search over Ethera world lore using ChromaDB.

This module is optional — if ChromaDB or sentence-transformers are not available,
the server falls back to simple keyword matching.

All heavy imports are lazy — they only load when initialize() is called.
"""

from pathlib import Path
from typing import Optional


class LoreSearcher:
    """Semantic search over the Ethera world lore.

    Uses ChromaDB + sentence-transformers when available.
    Falls back to keyword matching otherwise.
    """

    def __init__(self, world_root: str | Path, db_path: str | Path = "data/chroma_db"):
        self.world_root = Path(world_root)
        self.db_path = Path(db_path)
        self.collection = None
        self._initialized = False
        self._chroma_available = False
        self._st_available = False
        self._embedding_fn = None

    def _check_deps(self) -> bool:
        """Lazily check and import dependencies."""
        if not self._chroma_available:
            try:
                import chromadb  # noqa: F401
                self._chroma_available = True
            except Exception:
                self._chroma_available = False
        if not self._st_available:
            try:
                from sentence_transformers import SentenceTransformer
                self._st_available = True
            except Exception:
                self._st_available = False
        return self._chroma_available and self._st_available

    def initialize(self) -> bool:
        """Initialize ChromaDB and build index if needed. Returns True if successful."""
        if self._initialized:
            return True
        if not self._check_deps():
            return False
        try:
            import chromadb
            from chromadb.config import Settings

            client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(anonymized_telemetry=False),
            )
            self.collection = client.get_or_create_collection(
                name="ethera_lore",
                metadata={"hnsw:space": "cosine"},
            )
            # If collection is empty, build index
            if self.collection.count() == 0:
                self._build_index()
            self._initialized = True
            return True
        except Exception:
            return False

    def _build_index(self):
        """Index all .md files by ## heading sections."""
        chunks = []
        ids = []
        metadatas = []
        idx = 0

        for md_file in sorted(self.world_root.rglob("*.md")):
            rel_path = str(md_file.relative_to(self.world_root))
            text = md_file.read_text(encoding="utf-8")
            sections = self._split_sections(text, rel_path)
            for heading, content in sections:
                chunks.append(content)
                ids.append(f"{rel_path}#{idx}")
                metadatas.append({"source": rel_path, "heading": heading})
                idx += 1

        if chunks:
            self.collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas,
            )

    def _split_sections(self, text: str, source: str) -> list[tuple[str, str]]:
        """Split a .md file into sections by ## headings."""
        import re
        sections = []
        lines = text.split("\n")
        current_heading = "前言"
        current_lines = []

        for line in lines:
            if line.startswith("## "):
                if current_lines:
                    content = "\n".join(current_lines).strip()
                    if len(content) > 20:  # skip empty/minimal sections
                        sections.append((current_heading, f"# {source}  »  {current_heading}\n\n{content}"))
                current_heading = line.lstrip("# ").strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        # Last section
        if current_lines:
            content = "\n".join(current_lines).strip()
            if len(content) > 20:
                sections.append((current_heading, f"# {source}  »  {current_heading}\n\n{content}"))

        return sections

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Search lore. Returns list of {source, heading, content, score} dicts."""
        if self.collection is not None and self._initialized:
            return self._vector_search(query, top_k)
        return self._keyword_search(query, top_k)

    def _vector_search(self, query: str, top_k: int) -> list[dict]:
        """Vector similarity search."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
            )
            items = []
            for i in range(len(results["ids"][0])):
                items.append({
                    "source": results["metadatas"][0][i]["source"],
                    "heading": results["metadatas"][0][i]["heading"],
                    "content": results["documents"][0][i],
                    "score": float(results["distances"][0][i]) if results.get("distances") else 0,
                })
            return items
        except Exception:
            return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> list[dict]:
        """Simple keyword-based fallback search."""
        keywords = query.lower().split()
        results = []

        for md_file in sorted(self.world_root.rglob("*.md")):
            rel_path = str(md_file.relative_to(self.world_root))
            text = md_file.read_text(encoding="utf-8")
            text_lower = text.lower()

            match_count = sum(1 for kw in keywords if kw in text_lower)
            if match_count > 0:
                # Find the relevant section
                sections = self._split_sections(text, rel_path)
                for heading, content in sections:
                    content_lower = content.lower()
                    section_matches = sum(1 for kw in keywords if kw in content_lower)
                    if section_matches > 0:
                        results.append({
                            "source": rel_path,
                            "heading": heading,
                            "content": content,
                            "score": section_matches / len(keywords),
                        })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def status(self) -> dict:
        """Return the status of the lore search system."""
        return {
            "available": self._initialized and self.collection is not None,
            "chroma": self._chroma_available,
            "sentence_transformer": self._st_available,
            "document_count": self.collection.count() if self.collection else 0,
        }
