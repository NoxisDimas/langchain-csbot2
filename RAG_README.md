# RAG (Retrieval-Augmented Generation) System

Sistem RAG yang lengkap dengan fitur upload file, vector database, dan search capabilities.

## Fitur Utama

### 1. Document Processing
- **Supported File Types**: PDF, TXT, Markdown, CSV, Excel (XLSX/XLS), Word (DOCX/DOC), JSON, XML, HTML
- **Text Extraction**: Otomatis mengekstrak teks dari berbagai format file
- **Chunking**: Membagi dokumen menjadi chunks yang optimal untuk vector search

### 2. Vector Database
- **PostgreSQL + pgvector**: Menggunakan PostgreSQL dengan extension pgvector untuk penyimpanan vector
- **Schema Management**: Otomatis membuat schema untuk setiap knowledge base
- **Embedding Generation**: Mendukung OpenAI dan Ollama untuk pembuatan embeddings

### 3. Knowledge Base Management
- **Multiple Knowledge Bases**: Dapat membuat dan mengelola multiple knowledge bases
- **CRUD Operations**: Create, Read, Update, Delete untuk knowledge bases
- **Schema Isolation**: Setiap knowledge base memiliki schema terpisah

### 4. Search & Retrieval
- **Vector Similarity Search**: Pencarian berdasarkan similarity vector
- **Semantic Search**: Mencari berdasarkan makna, bukan hanya kata kunci
- **Configurable Results**: Dapat mengatur jumlah hasil pencarian

### 5. Frontend Interface
- **Modern UI**: Interface yang user-friendly dengan React
- **File Upload**: Drag & drop atau click to upload
- **Real-time Stats**: Monitoring stats vectorstore
- **Search Interface**: Interface pencarian yang intuitif

## Arsitektur Sistem

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Embedding     │
                       │   Service       │
                       │   (OpenAI/      │
                       │   Ollama)       │
                       └─────────────────┘
```

## Setup dan Instalasi

### 1. Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ dengan extension pgvector
- OpenAI API key (opsional, bisa menggunakan Ollama)

### 2. Database Setup
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE DATABASE rag_database;
```

### 3. Backend Setup
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Set DATABASE_URL dan OPENAI_API_KEY/OLLAMA_BASE_URL
python -m uvicorn app.main:app --reload
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Knowledge Base Management
- `POST /api/rag/knowledge-bases` - Create knowledge base
- `GET /api/rag/knowledge-bases` - List all knowledge bases
- `DELETE /api/rag/knowledge-bases/{name}` - Delete knowledge base

### Document Management (RAG-only)
- `POST /api/rag/upload` - Upload dan ingest chunks ke vectorstore

### Search
- `POST /api/rag/search` - Search documents using vector similarity

### System
- `GET /api/rag/stats` - Get vectorstore statistics
- `GET /api/rag/health` - Health check

## Penggunaan

### 1. Membuat Knowledge Base
1. Buka interface RAG System
2. Pilih tab "Manage"
3. Masukkan nama dan deskripsi knowledge base
4. Klik "Create"

### 2. Upload File
1. Pilih tab "Upload Files"
2. Pilih knowledge base yang akan digunakan
3. Klik "Choose File" dan pilih file yang akan diupload
4. Klik "Upload File"
5. File akan di-chunk dan di-ingest ke vectorstore

### 3. Search Documents
1. Pilih tab "Search"
2. Masukkan query pencarian
3. Klik "Search"
4. Hasil pencarian akan ditampilkan dengan similarity score

### 4. Monitor Statistics
1. Pilih tab "Statistics"
2. Lihat stats vectorstore

## Security Considerations
- Validasi tipe dan ukuran file, sanitasi nama file
- Rate limiting & HTTPS di production
- Connection pooling untuk database

## License

MIT License - lihat LICENSE file untuk detail.