# RAG System Guide

## Overview

The new RAG (Retrieval-Augmented Generation) system has been completely redesigned to be simpler, more maintainable, and easier to use. It uses **PGVector** from LangChain for vector storage and supports multiple file types.

## Architecture

```
📁 uploads/           # File storage folder
├── 📄 document1.pdf
├── 📄 document2.docx
└── 📄 data.csv

🔧 VectorStore        # Core vector store class
├── 📄 vector_store.py
├── 📄 loader.py
├── 📄 retriever.py
└── 📄 ingest.py

🌐 API Endpoints      # REST API
├── POST /api/rag/upload
├── POST /api/rag/ingest
├── POST /api/rag/search
├── GET /api/rag/search/filter
├── GET /api/rag/stats
├── GET /api/rag/health
├── GET /api/rag/files
└── DELETE /api/rag/files/{filename}
```

## Supported File Types

- **Text Files** (`.txt`) - Plain text documents
- **CSV Files** (`.csv`) - Comma-separated values
- **PDF Files** (`.pdf`) - Portable Document Format
- **Word Documents** (`.docx`) - Microsoft Word files
- **Excel Files** (`.xlsx`) - Microsoft Excel spreadsheets
- **Markdown Files** (`.md`) - Markdown documents

## Quick Start

### 1. Setup Environment

Make sure your `.env` file has the required configuration:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DB_SCHEMA=ai_cs

# LLM Provider (choose one)
OPENAI_API_KEY=your_openai_key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b-instruct
OLLAMA_EMBED_MODEL=nomic-embed-text
```

### 2. Upload Documents

```bash
# Upload a file
curl -X POST "http://localhost:8000/api/rag/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf"
```

### 3. Ingest Documents

```bash
# Ingest all files from uploads folder
curl -X POST "http://localhost:8000/api/rag/ingest?update_existing=true"
```

### 4. Search Documents

```bash
# Search for relevant documents
curl -X POST "http://localhost:8000/api/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "limit": 5
  }'
```

## API Reference

### Upload File

**Endpoint:** `POST /api/rag/upload`

Upload a file to the uploads folder.

**Request:**
- `file`: File to upload (multipart/form-data)

**Response:**
```json
{
  "filename": "document.pdf",
  "status": "uploaded",
  "message": "File document.pdf uploaded successfully to uploads folder."
}
```

### Ingest Documents

**Endpoint:** `POST /api/rag/ingest`

Process all files in the uploads folder and add them to the vector store.

**Query Parameters:**
- `update_existing` (boolean): Whether to update existing documents with same titles

**Response:**
```json
{
  "status": "success",
  "message": "Documents ingested successfully into vector store",
  "update_existing": true
}
```

### Search Documents

**Endpoint:** `POST /api/rag/search`

Search for documents using vector similarity.

**Request Body:**
```json
{
  "query": "Your search query",
  "limit": 5
}
```

**Response:**
```json
[
  {
    "content": "Document content...",
    "metadata": {
      "title": "Document Title",
      "category": "pdf file",
      "source": "/path/to/file.pdf"
    },
    "similarity_score": 0.85
  }
]
```

### Filter Documents

**Endpoint:** `GET /api/rag/search/filter`

Filter documents by metadata.

**Query Parameters:**
- `key`: Metadata key to filter by (`category`, `title`, `source`)
- `value`: Value to search for
- `k`: Maximum number of results (default: 100)
- `offset`: Number of results to skip (default: 0)

**Response:**
```json
{
  "results": [
    {
      "content": "Document content...",
      "metadata": {...},
      "similarity_score": 0.85
    }
  ],
  "total": 1,
  "filter": {"category": "pdf file"}
}
```

### Get Statistics

**Endpoint:** `GET /api/rag/stats`

Get vector store statistics.

**Response:**
```json
{
  "collection_name": "ai_cs",
  "database_url": "localhost:5432",
  "embedding_model": "OllamaEmbeddings(model='nomic-embed-text')",
  "uploads_folder": "/path/to/uploads",
  "files_count": 5
}
```

### Health Check

**Endpoint:** `GET /api/rag/health`

Check system health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "services": {
    "database": "connected",
    "vector_store": "available",
    "embedding_model": "available"
  },
  "stats": {...}
}
```

### List Files

**Endpoint:** `GET /api/rag/files`

List all files in the uploads folder.

**Response:**
```json
{
  "files": [
    {
      "filename": "document.pdf",
      "size": 1024000,
      "modified": "2024-01-01T12:00:00",
      "extension": ".pdf"
    }
  ]
}
```

### Delete File

**Endpoint:** `DELETE /api/rag/files/{filename}`

Delete a file from the uploads folder.

**Response:**
```json
{
  "status": "success",
  "message": "File document.pdf deleted successfully"
}
```

## Python Usage

### Using VectorStore Class

```python
from app.services.rag.vector_store import VectorStore

# Initialize vector store
vector_store = VectorStore()

# Build vector store from uploads folder
vector_store.build_vector_store(update_existing=True)

# Search for documents
results = vector_store.similarity_search("your query", k=5)

# Filter by metadata
filtered_results = vector_store.filter_by_metadata("category", "pdf file", k=10)

# Get statistics
stats = vector_store.get_collection_stats()
```

### Using Retriever Functions

```python
from app.services.rag.retriever import retrieve_knowledge, retrieve_knowledge_with_scores

# Retrieve documents
docs = retrieve_knowledge("your query")

# Retrieve with scores
results = retrieve_knowledge_with_scores("your query", k=5)

# Filter by metadata
filtered = filter_knowledge_by_metadata("category", "pdf file")
```

### Using Ingest Functions

```python
from app.services.rag.ingest import ingest_documents, get_ingestion_stats

# Ingest documents
success = ingest_documents(update_existing=True)

# Get stats
stats = get_ingestion_stats()
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `DB_SCHEMA` | Database schema name | `ai_cs` |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.1:8b-instruct` |
| `OLLAMA_EMBED_MODEL` | Ollama embedding model | `nomic-embed-text` |

### Vector Store Settings

The vector store uses these default settings:

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Similarity Search**: Top 5 results by default
- **Collection**: Uses `DB_SCHEMA` as collection name

## Testing

Run the test script to verify the RAG system:

```bash
python test_new_rag_system.py
```

This will test:
- Health check
- File upload
- Document ingestion
- Search functionality
- Filter functionality
- Statistics

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check `DATABASE_URL` in `.env`
   - Ensure PostgreSQL is running
   - Verify pgvector extension is installed

2. **File Upload Fails**
   - Check file type is supported
   - Ensure uploads folder exists and is writable
   - Verify file is not empty

3. **Ingestion Fails**
   - Check embedding model is available
   - Verify database connection
   - Check file formats are supported

4. **Search Returns No Results**
   - Ensure documents were ingested successfully
   - Check if query is relevant to ingested content
   - Verify vector store is properly initialized

### Logs

The system provides detailed logging with emojis for easy identification:

- 🔧 Processing operations
- ✅ Successful operations
- ❌ Errors
- 🔍 Search operations
- 📚 Document operations
- 📦 Vector store operations
- 🗑️ Deletion operations

## Migration from Old System

If you're migrating from the old RAG system:

1. **Backup your data** - Export any important documents
2. **Update your code** - Replace old API calls with new endpoints
3. **Test thoroughly** - Use the test script to verify functionality
4. **Update documentation** - Update any references to old endpoints

## Performance Tips

1. **Batch Processing**: Upload multiple files before ingesting
2. **Chunk Size**: Adjust chunk size based on your content type
3. **Indexing**: Consider database indexing for large collections
4. **Caching**: Implement caching for frequently searched queries

## Security Considerations

1. **File Validation**: Always validate uploaded files
2. **Access Control**: Implement proper authentication/authorization
3. **Data Privacy**: Be aware of PII in uploaded documents
4. **Rate Limiting**: Consider implementing rate limiting for API endpoints