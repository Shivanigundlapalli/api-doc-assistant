# API Documentation Assistant (Production Edition)

A production-grade, RAG-based AI assistant for API documentation. It features a modern SaaS UI, clean architecture, multi-format document support, advanced retrieval, and full observability using LangSmith.

## Features

- **Multi-Format Support**: Automatically parses `.md`, `.pdf`, `.html`, `.json` (Swagger), and `.yaml`.
- **Advanced Retrieval**: Uses ChromaDB with MMR (Maximal Marginal Relevance), deduplication, and similarity score thresholds.
- **Enterprise UI**: A beautiful, responsive interface featuring Dark/Light modes, animations, and clean layouts.
- **Guardrails & Query Rewriting**: Blocks harmful queries and optimizes vague questions using an LLM.
- **Evaluation Pipeline**: Integrated with LangSmith for full tracing and observability.
- **Exporting**: Save chat history as PDF or Markdown.

## Clean Architecture

The codebase has been refactored for enterprise-level maintainability:

```
api-doc-assistant/
├── app.py                     # Main Streamlit Application
├── main.py                    # Evaluation/CLI entry point
├── components/                # UI Components (Sidebar, Hero, Chat, Styling)
├── services/                  # Business Logic (LLM, Vector DB, Eval)
├── utils/                     # Utilities (Loaders, Text Splitters, Exporters)
├── prompts/                   # System Prompts (QA, Rewrite, Guardrails)
├── data/                      # Exported chat histories
└── docs/                      # Source documents
```

## Quick Start

1. **Clone and Install**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=api-doc-assistant
   LANGCHAIN_API_KEY=your_langsmith_key
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

4. **Run Evaluation Pipeline**
   ```bash
   python main.py
   ```

## Deployment

### Docker
1. Create a `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```
2. Build and run:
   ```bash
   docker build -t api-doc-assistant .
   docker run -p 8501:8501 --env-file .env api-doc-assistant
   ```

### Streamlit Cloud
1. Push to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/).
3. Connect repository and add Secrets (e.g., `GOOGLE_API_KEY`).
4. Deploy!

### Render / Railway
1. Connect GitHub repo.
2. Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3. Add environment variables.