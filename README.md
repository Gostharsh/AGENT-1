README Project Description
Multi-PDF RAG Assistant

A Retrieval-Augmented Generation (RAG) system built with Python, ChromaDB, and Ollama that allows users to query multiple PDF documents using natural language.

The system automatically:

Loads multiple PDF files
Extracts and chunks text
Stores document chunks in ChromaDB
Performs semantic similarity search
Retrieves relevant context from multiple documents
Generates accurate answers using a local LLM (Llama 3.2 via Ollama)
Displays source PDF names and page references
Features
Multi-PDF support
Semantic document search
Local LLM inference with Ollama
ChromaDB vector database integration
Configurable chunk size and overlap
Source-aware responses
Modular and scalable architecture
Production-ready error handling


Tech Stack

Python
ChromaDB
Ollama
Llama 3.2
PyPDF
Requests
Pathlib


Architecture

PDF Files
    │
    ▼
Text Extraction
    │
    ▼
Chunking
    │
    ▼
ChromaDB Vector Store
    │
    ▼
Semantic Retrieval
    │
    ▼
Context Builder
    │
    ▼
Llama 3.2 (Ollama)
    │
    ▼
Answer + Source References
