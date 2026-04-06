# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Local RAG (Retrieval Augmented Generation) chatbot that runs entirely on the local machine using Ollama, Streamlit, and DeepSeek-R1. The chatbot answers questions based on indexed PDF documents.

## Prerequisites

- Python 3.7+
- Ollama installed and running (`ollama serve` in a separate terminal)
- Required models pulled in Ollama:
  - `ollama pull deepseek-r1` (chat model)
  - `ollama pull nomic-embed-text` (embeddings)

## Commands

```bash
# Install dependencies
pip install -r src/requirements.txt

# Load/index documents into ChromaDB (update data_path in load_docs.py first)
python src/load_docs.py

# Reset vector database
python src/load_docs.py --reset

# Run the Streamlit chatbot
streamlit run src/UI.py
```

## Architecture

```
src/
├── UI.py           # Streamlit chat interface - calls query_rag()
├── rag_query.py    # RAG logic: queries ChromaDB, builds prompt, calls Ollama
├── embedding.py    # Returns OllamaEmbeddings (nomic-embed-text)
└── load_docs.py    # PDF loading, chunking (800/80), and ChromaDB indexing

data/               # Place PDF documents here
chroma/             # ChromaDB vector store (created after loading docs)
```

## Key Configuration Points

- **LLM Model**: `rag_query.py:47` - currently `deepseek-r1`, alternatives commented out (mistral, llama3)
- **Embedding Model**: `embedding.py:10` - currently `nomic-embed-text`
- **RAG Prompt Template**: `rag_query.py:10-18` - modify for different chatbot behavior
- **Document Path**: `load_docs.py:15` - hardcoded path that must be updated before loading docs
- **Retrieval Settings**: `rag_query.py:39` - `k=5` documents retrieved per query
- **Chunking Settings**: `load_docs.py:28-33` - chunk_size=800, chunk_overlap=80
