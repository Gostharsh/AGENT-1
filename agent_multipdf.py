from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import chromadb
import requests
from chromadb.api.models.Collection import Collection
from pypdf import PdfReader

# ==========================================================
# CONFIG
# ==========================================================

PDF_FOLDER = Path(os.getenv("PDF_FOLDER", r"D:\GEN_AI\pdfs"))
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "multi_pdf_rag")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 300))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "llama3.2"
)

TOP_K = int(os.getenv("TOP_K", 5))

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ==========================================================
# PDF PROCESSOR
# ==========================================================


class PDFProcessor:

    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int,
        overlap: int
    ) -> list[str]:

        words = text.split()

        if len(words) <= chunk_size:
            return [text]

        step = chunk_size - overlap

        return [
            " ".join(words[i:i + chunk_size])
            for i in range(0, len(words), step)
        ]

    def extract(
        self,
        pdf_folder: Path
    ) -> tuple[list[str], list[dict], list[str]]:

        documents: list[str] = []
        metadatas: list[dict] = []
        ids: list[str] = []

        chunk_id = 1

        pdf_files = list(pdf_folder.glob("*.pdf"))

        if not pdf_files:
            raise FileNotFoundError(
                f"No PDFs found in {pdf_folder}"
            )

        for pdf_file in pdf_files:

            logger.info(
                "Processing %s",
                pdf_file.name
            )

            try:
                reader = PdfReader(str(pdf_file))

                for page_no, page in enumerate(
                    reader.pages,
                    start=1
                ):

                    text = page.extract_text()

                    if not text:
                        continue

                    chunks = self.chunk_text(
                        text=text,
                        chunk_size=CHUNK_SIZE,
                        overlap=CHUNK_OVERLAP
                    )

                    for chunk in chunks:

                        documents.append(chunk)

                        metadatas.append(
                            {
                                "source": pdf_file.name,
                                "page": page_no
                            }
                        )

                        ids.append(str(chunk_id))

                        chunk_id += 1

            except Exception as error:
                logger.error(
                    "Failed reading %s : %s",
                    pdf_file.name,
                    error
                )

        logger.info(
            "Indexed %s chunks",
            len(documents)
        )

        return documents, metadatas, ids


# ==========================================================
# VECTOR DATABASE
# ==========================================================


class VectorStore:

    def __init__(self) -> None:

        client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection: Collection = (
            client.get_or_create_collection(
                name=COLLECTION_NAME
            )
        )

    def load(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str]
    ) -> None:

        if self.collection.count() > 0:

            logger.info(
                "Collection already contains %s chunks",
                self.collection.count()
            )

            return

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(
            "Added %s chunks",
            len(documents)
        )

    def search(
        self,
        query: str,
        top_k: int = TOP_K
    ) -> dict[str, Any]:

        return self.collection.query(
            query_texts=[query],
            n_results=top_k
        )


# ==========================================================
# OLLAMA CLIENT
# ==========================================================


class OllamaClient:

    @staticmethod
    def generate(
        prompt: str
    ) -> str:

        try:

            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0
                },
                timeout=120
            )

            response.raise_for_status()

            return response.json()["response"]

        except requests.RequestException as error:

            logger.error(
                "Ollama request failed: %s",
                error
            )

            return str(error)


# ==========================================================
# RAG ENGINE
# ==========================================================


class RAGEngine:

    def __init__(
        self,
        store: VectorStore
    ) -> None:

        self.store = store
        self.last_question = ""

    def rewrite_query(
        self,
        current_question: str
    ) -> str:

        if not self.last_question:
            return current_question

        prompt = f"""
    Previous Question:
    {self.last_question}

    Current Question:
    {current_question}

    Rewrite the current question
    so it is fully self-contained.

    Keep the meaning exactly the same.

    Return ONLY the rewritten question.
    """

        rewritten = OllamaClient.generate(prompt)

        return rewritten.strip()

    def is_followup(
        self,
        question: str
    ) -> bool:

        followup_words = {
            "it",
            "its",
            "they",
            "them",
            "this",
            "that",
            "those"
        }

        words = question.lower().split()

        return any(
            word in followup_words
            for word in words
        )

    def ask(
        self,
        question: str
    ) -> str:

        original_question = question

        if self.is_followup(question):

            question = self.rewrite_query(
                question
            )

            print(
                "\n[REWRITTEN QUERY]"
            )

            print(question)

        results = self.store.search(question)

        context = "\n\n".join(
            (
                f"Source: {meta['source']}\n"
                f"Page: {meta['page']}\n\n"
                f"{doc}"
            )
            for doc, meta in zip(
                results["documents"][0],
                results["metadatas"][0]
            )
        )

        prompt = f"""
You are a document assistant.

Answer ONLY using the provided context.

Keep the answer concise.

Mention:
- PDF name
- Page number

Context:
{context}

Question:
{question}

Answer:
"""

        answer = OllamaClient.generate(prompt)

        self.last_question = original_question

        return answer

        # return OllamaClient.generate(prompt)


# ==========================================================
# MAIN
# ==========================================================


def main() -> None:

    processor = PDFProcessor()

    documents, metadatas, ids = (
        processor.extract(PDF_FOLDER)
    )

    store = VectorStore()

    store.load(
        documents,
        metadatas,
        ids
    )

    rag = RAGEngine(store)

    while True:

        question = input("\nAsk: ").strip()

        if question.lower() in {
            "exit",
            "quit"
        }:
            break

        answer = rag.ask(question)

        print("\n")
        print(answer)
        print()


if __name__ == "__main__":
    main()
