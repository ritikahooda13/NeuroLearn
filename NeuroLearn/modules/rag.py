"""
Retrieval-Augmented Generation (RAG) Module
Upload PDFs / Notes → Chunk → Embed → Retrieve → Grounded answers
"""

import os
import fitz  # PyMuPDF
from typing import List, Dict, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import hashlib


class DocumentRAG:
    """
    Lightweight RAG system for educational documents.
    Uses SentenceTransformers + FAISS-like numpy search (no heavy DB needed for demo).
    """

    def __init__(self, persist_dir: str = "data/rag_store"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self.embedder = None
        self.chunks: List[str] = []
        self.embeddings: Optional[np.ndarray] = None
        self.metadata: List[Dict] = []
        self.sources: List[str] = []

        self._load()

    def _get_embedder(self):
        if self.embedder is None:
            # Lightweight & fast model
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        return self.embedder

    def _load(self):
        meta_path = os.path.join(self.persist_dir, "meta.json")
        emb_path = os.path.join(self.persist_dir, "embeddings.npy")
        if os.path.exists(meta_path) and os.path.exists(emb_path):
            try:
                with open(meta_path, "r") as f:
                    data = json.load(f)
                    self.chunks = data.get("chunks", [])
                    self.metadata = data.get("metadata", [])
                    self.sources = data.get("sources", [])
                self.embeddings = np.load(emb_path)
            except Exception:
                pass

    def _save(self):
        with open(os.path.join(self.persist_dir, "meta.json"), "w") as f:
            json.dump({
                "chunks": self.chunks,
                "metadata": self.metadata,
                "sources": self.sources
            }, f)
        if self.embeddings is not None:
            np.save(os.path.join(self.persist_dir, "embeddings.npy"), self.embeddings)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n\n"
        doc.close()
        return text

    def add_document(self, file_path: str, source_name: str = None) -> int:
        """Add a PDF or text file. Returns number of chunks added."""
        source_name = source_name or os.path.basename(file_path)

        if file_path.lower().endswith(".pdf"):
            text = self.extract_text_from_pdf(file_path)
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        if not text.strip():
            return 0

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        new_chunks = splitter.split_text(text)

        embedder = self._get_embedder()
        new_embeddings = embedder.encode(new_chunks, show_progress_bar=False)

        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        for i, chunk in enumerate(new_chunks):
            self.chunks.append(chunk)
            self.metadata.append({
                "source": source_name,
                "chunk_id": len(self.chunks) - 1
            })

        if source_name not in self.sources:
            self.sources.append(source_name)

        self._save()
        return len(new_chunks)

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict]:
        if not self.chunks or self.embeddings is None:
            return []

        embedder = self._get_embedder()
        q_emb = embedder.encode([query])[0]

        # Cosine similarity
        norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q_emb)
        similarities = np.dot(self.embeddings, q_emb) / (norms + 1e-9)

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "text": self.chunks[idx],
                "source": self.metadata[idx]["source"],
                "score": float(similarities[idx])
            })
        return results

    def get_context(self, query: str, top_k: int = 4) -> str:
        docs = self.retrieve(query, top_k)
        if not docs:
            return ""

        context = "=== RELEVANT COURSE MATERIAL ===\n\n"
        for i, d in enumerate(docs, 1):
            context += f"[Source: {d['source']} | Relevance: {d['score']:.2f}]\n{d['text']}\n\n"
        context += "=== END MATERIAL ===\n"
        return context

    def clear(self):
        self.chunks = []
        self.embeddings = None
        self.metadata = []
        self.sources = []
        self._save()

    def status(self) -> Dict:
        return {
            "num_chunks": len(self.chunks),
            "num_sources": len(self.sources),
            "sources": self.sources
        }
