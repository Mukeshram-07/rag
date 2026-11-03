from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
import openpyxl
import pymupdf
import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DocumentChunk:
    text: str
    source: str
    location: str


class OllamaEmbeddingFunction:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def name(self) -> str:
        return f"ollama-{self.model}"

    def __call__(self, input: list[str]) -> list[list[float]]:
        response = requests.post(
            f"{self.base_url}/api/embed",
            json={"model": self.model, "input": input},
            timeout=120,
        )
        response.raise_for_status()
        embeddings = response.json().get("embeddings")
        if not embeddings:
            raise RuntimeError("Ollama returned no embeddings.")
        return embeddings

    def embed_query(self, input: list[str]) -> list[list[float]]:
        return self(input)


class RAGEngine:
    def __init__(self) -> None:
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.chat_model = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2")
        self.embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        chroma_dir = Path(os.getenv("CHROMA_DIR", "./data/chroma"))
        chroma_dir.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(chroma_dir))
        self.collection = client.get_or_create_collection(
            name="knowledge",
            embedding_function=OllamaEmbeddingFunction(self.base_url, self.embed_model),
            metadata={"hnsw:space": "cosine"},
        )

    @staticmethod
    def _chunks(text: str, size: int = 900, overlap: int = 150) -> list[str]:
        normalized = " ".join(text.split())
        if not normalized:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(start + size, len(normalized))
            if end < len(normalized):
                boundary = normalized.rfind(" ", start, end)
                end = boundary if boundary > start else end
            chunks.append(normalized[start:end].strip())
            if end >= len(normalized):
                break
            start = max(end - overlap, start + 1)
        return chunks

    def parse_file(self, path: Path) -> list[DocumentChunk]:
        suffix = path.suffix.lower()
        chunks: list[DocumentChunk] = []
        if suffix == ".pdf":
            with pymupdf.open(path) as document:
                for page_number, page in enumerate(document, start=1):
                    for text in self._chunks(page.get_text()):
                        chunks.append(DocumentChunk(text, path.name, f"page {page_number}"))
        elif suffix in {".xlsx", ".xlsm"}:
            workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
            for sheet in workbook.worksheets:
                rows = []
                for row in sheet.iter_rows(values_only=True):
                    values = [str(value).strip() for value in row if value is not None and str(value).strip()]
                    if values:
                        rows.append(" | ".join(values))
                for index, text in enumerate(self._chunks("\n".join(rows)), start=1):
                    chunks.append(DocumentChunk(text, path.name, f"sheet {sheet.title}, section {index}"))
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}. Upload PDF or Excel files.")
        return chunks

    def index_file(self, path: Path) -> int:
        chunks = self.parse_file(path)
        if not chunks:
            return 0
        file_id = hashlib.sha256(path.read_bytes()).hexdigest()
        self.collection.delete(where={"file_id": file_id})
        self.collection.add(
            ids=[f"{file_id}-{index}" for index in range(len(chunks))],
            documents=[chunk.text for chunk in chunks],
            metadatas=[
                {"source": chunk.source, "location": chunk.location, "file_id": file_id}
                for chunk in chunks
            ],
        )
        return len(chunks)

    def indexed_files(self) -> list[str]:
        data = self.collection.get(include=["metadatas"])
        return sorted({item["source"] for item in (data.get("metadatas") or [])})

    def clear(self) -> None:
        for item in self.indexed_files():
            metadata = self.collection.get(where={"source": item}, include=["metadatas"])
            file_ids = {row["file_id"] for row in (metadata.get("metadatas") or [])}
            for file_id in file_ids:
                self.collection.delete(where={"file_id": file_id})

    def answer(self, question: str, history: list[dict[str, str]], top_k: int = 5) -> tuple[str, list[dict[str, Any]]]:
        if self.collection.count() == 0:
            raise RuntimeError(
                "No restaurant documents are indexed. Upload and index a PDF or Excel file first."
            )
        results = self.collection.query(query_texts=[question], n_results=top_k)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        context = "\n\n".join(
            f"[{index + 1}] {metadata['source']} ({metadata['location']}):\n{document}"
            for index, (document, metadata) in enumerate(zip(documents, metadatas))
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a precise restaurant business assistant. Answer questions about "
                    "menus, recipes, ingredients, inventory, sales, staffing, costs, suppliers, "
                    "and restaurant operations using only the supplied context. "
                    "If the context does not contain the answer, say you do not know. "
                    "Do not invent prices, quantities, policies, or business metrics. "
                    "Cite sources like [1] or [2]."
                ),
            },
            *history[-6:],
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ]
        response = requests.post(
            f"{self.base_url.rstrip('/')}/api/chat",
            json={"model": self.chat_model, "messages": messages, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        answer = response.json().get("message", {}).get("content", "").strip()
        if not answer:
            raise RuntimeError("Ollama returned an empty answer.")
        return answer, [
            {"source": metadata["source"], "location": metadata["location"], "text": document}
            for document, metadata in zip(documents, metadatas)
        ]
