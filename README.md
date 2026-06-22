# API Documentation Assistant

> A Retrieval-Augmented Generation (RAG) app that answers questions from your API documentation using LangChain, Google Gemini, ChromaDB, and Streamlit.

## Project Overview

API Documentation Assistant is an AI-powered documentation helper built for teams and developers who want fast, grounded answers from their docs. It loads Markdown and PDF content, splits it into searchable chunks, stores embeddings in ChromaDB, and uses Gemini 2.5 Flash to generate responses that stay anchored to retrieved context.

The goal of the project is simple: ask a question about your documentation and get a relevant answer without hallucinations. The Streamlit interface also shows the retrieved source context so you can verify where each answer came from.

## Features

- Loads API documentation from Markdown and PDF files
- Splits documents into chunks using `RecursiveCharacterTextSplitter`
- Generates semantic embeddings with Gemini Embeddings
- Stores vectors in ChromaDB for persistent retrieval
- Performs semantic similarity search over documentation chunks
- Uses Gemini 2.5 Flash to generate grounded answers
- Streamlit-based web interface for an interactive experience
- Displays retrieved sources alongside answers
- Reduces hallucinations by answering only from retrieved documentation

## System Architecture Diagram

```text
User Question
     |
     v
Streamlit App (app.py)
     |
     v
Chroma Retriever <-----------------------------+
     |                                         |
     v                                         |
Relevant Documentation Chunks                  |
     |                                         |
     v                                         |
Gemini 2.5 Flash + Prompt Guardrails           |
     |                                         |
     v                                         |
Grounded Answer + Retrieved Sources -----------+
```

## Project Structure

```text
api-doc-assistant/
├── chroma_db/
├── docs/
│   ├── api_guide.pdf
│   └── authentication.md
├── .env
├── app.py
├── main.py
├── requirements.txt
└── test_questions.txt
```

### What each file does

- `app.py` - Streamlit web app for asking questions and viewing answers
- `main.py` - CLI-based RAG flow for testing the retrieval pipeline from the terminal
- `docs/` - Source documentation used to build the knowledge base
- `chroma_db/` - Persisted ChromaDB vector store
- `requirements.txt` - Python dependencies
- `.env` - Environment variables for Gemini authentication
- `test_questions.txt` - Optional prompt ideas and test questions

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd api-doc-assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

On Windows:

```bash
.venv\\Scripts\\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables Setup

Create a `.env` file in the project root and add your Gemini API key:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

Optional environment variables can be added later if you expand the project, but the current app primarily depends on `GOOGLE_API_KEY`.

## Running the Application

### Run the Streamlit web app

```bash
streamlit run app.py
```

### Run the CLI version

```bash
python main.py
```

The Streamlit app is the recommended way to use the project. The CLI script is useful for quick terminal-based testing of the RAG workflow.

## Example Questions

Here are some example questions you can ask:

- How do I authenticate?
- How do I generate an API key?
- What is the expiration policy for API keys?
- How do I use the API key in a request?
- What does a 401 Unauthorized error mean?
- What does a 403 Forbidden error mean?

## How RAG Works in This Project

1. Documentation files are loaded from the `docs/` folder.
2. The text is split into smaller chunks using `RecursiveCharacterTextSplitter`.
3. Each chunk is converted into embeddings with Gemini Embeddings.
4. Embeddings are stored in ChromaDB for persistent semantic search.
5. When a user asks a question, the app retrieves the most relevant chunks.
6. The retrieved context is passed to Gemini 2.5 Flash with strict instructions to answer only from the documentation.
7. The answer is shown in the UI together with the retrieved source context.

This RAG pattern improves accuracy by grounding the model in your documentation instead of relying on general world knowledge.

## Technologies Used

- Python
- LangChain
- Google Gemini 2.5 Flash
- Gemini Embeddings
- ChromaDB
- Streamlit
- python-dotenv

## Future Improvements

- Add multi-file ingestion from larger documentation sets
- Support document upload directly from the UI
- Add citation metadata for chunk-level traceability
- Improve chunking strategies for long technical PDFs
- Add conversation memory for follow-up questions
- Build a polished document indexing pipeline with progress feedback
- Add evaluation tests for answer grounding and retrieval quality

## Author

**Shivanigundlapalli**

If you found this project useful, feel free to fork it, adapt it to your own documentation, and use it as a portfolio project for RAG-based applications.