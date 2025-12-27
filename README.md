# GraphRAG vs. Conventional RAG: Codebase Q&A Demo

This is a demonstration repository designed to evaluate and showcase the effectiveness of **GraphRAG** against conventional RAG systems. It allows for side-by-side comparison of retrieval strategies including AST-based, Code-specific, and Recursive chunking.

## Overview

This system allows you to upload or point to a Python codebase, index it using various strategies, and compare how different RAG architectures handle complex source code queries. It includes a sophisticated hallucination detection mechanism (SelfCheckGPT) to further validate the reliability of each approach.

### Key Features

- **Multi-Strategy Chunking**: Optimize retrieval by choosing between `AST`, `Code`, or `Recursive` chunking.
- **Hallucination Self-Check**: Uses a `SelfCheckGPT`-inspired approach to verify generated answers by comparing them against sampled responses and calculating embedding similarity.
- **RAG Agent**: Built on LangGraph to provide structured reasoning and document retrieval.
- **Integrated Architecture**: A FastAPI backend coupled with a modern React + Tailwind CSS frontend.
- **Vector Search**: Persistent indexing using ChromaDB and HuggingFace embeddings.

## Setup & Installation

### Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)
- [UV](https://github.com/astral-sh/uv) (Python package manager)
- [Node.js & npm](https://nodejs.org/) (for Frontend)
- An AI Provider API Key (e.g., Groq)

### 1. Backend Configuration

Clone the repository and install dependencies:

```powershell
uv sync
```

Create a `.env` file by copying the example and filling in your API keys:

```powershell
cp .env.example .env
```

Your `.env` file should contain:

- `GROQ_API_KEY`: Required for LLM access.
- `LANGSMITH_API_KEY`: Optional, for tracing and debugging.
- `LANGSMITH_TRACING`: Set to `true` to enable LangSmith.

### 2. Frontend Configuration

Navigate to the frontend directory and install dependencies:

```powershell
cd src/frontend
npm install
```

## Running the Application

You can start both the Backend (FastAPI) and Frontend (Vite) simultaneously using the convenience script:

```powershell
python start.py
```

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Testing the Self-Check

1. **Upload your codebase** by clicking the upload icon in the sidebar and selecting a `.zip` file containing your Python code.
2. **Select the database** (collection) that was just created from the header dropdown.
3. **Ask a question** about your code (e.g., "What does the Calculator class do?").
4. Once the answer is generated, click the **"Self Check"** (Shield icon) button.
5. The system will generate a secondary "sampled" response internally and show you a **Similarity Score**. If the score is low (<= 50%), it will flag a potential hallucination.

## P4 (GraphRAG)

The next phase of development (P4) will introduce Knowledge Graph integration to improve retrieval for complex, cross-module relationship queries.
