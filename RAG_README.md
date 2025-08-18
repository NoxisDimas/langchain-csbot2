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
- **CRUD Operations**: Create, Read, Update, Delete untuk knowledge bases dan documents
- **Schema Isolation**: Setiap knowledge base memiliki schema terpisah

### 4. Search & Retrieval
- **Vector Similarity Search**: Pencarian berdasarkan similarity vector
- **Semantic Search**: Mencari berdasarkan makna, bukan hanya kata kunci
- **Configurable Results**: Dapat mengatur jumlah hasil pencarian

### 5. Frontend Interface
- **Modern UI**: Interface yang user-friendly dengan React
- **File Upload**: Drag & drop atau click to upload
- **Real-time Stats**: Monitoring progress dan statistics
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
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create database (jika belum ada)
CREATE DATABASE rag_database;
```

### 3. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env file dengan konfigurasi yang sesuai
# DATABASE_URL=postgresql://username:password@localhost:5432/rag_database
# OPENAI_API_KEY=your_openai_api_key_here

# Run migrations (akan otomatis dibuat saat startup)
python -m uvicorn app.main:app --reload
```

### 4. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## API Endpoints

### Knowledge Base Management
- `POST /api/rag/knowledge-bases` - Create knowledge base
- `GET /api/rag/knowledge-bases` - List all knowledge bases
- `DELETE /api/rag/knowledge-bases/{name}` - Delete knowledge base

### Document Management
- `POST /api/rag/upload` - Upload and process file
- `GET /api/rag/documents` - List all documents
- `DELETE /api/rag/documents/{id}` - Delete document

### Search
- `POST /api/rag/search` - Search documents using vector similarity

### System
- `GET /api/rag/stats` - Get system statistics
- `POST /api/rag/process-embeddings` - Process pending embeddings
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
5. File akan diproses dan embeddings akan dibuat secara otomatis

### 3. Search Documents
1. Pilih tab "Search"
2. Masukkan query pencarian
3. Klik "Search"
4. Hasil pencarian akan ditampilkan dengan similarity score

### 4. Monitor Statistics
1. Pilih tab "Statistics"
2. Lihat overview sistem:
   - Jumlah knowledge bases
   - Jumlah documents
   - Progress embeddings
   - Completion percentage

## Konfigurasi

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/rag_database

# OpenAI (untuk embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# Ollama (alternatif untuk embeddings lokal)
OLLAMA_BASE_URL=http://localhost:11434

# LangSmith (opsional, untuk monitoring)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=rag-system
```

### Chunking Configuration
```python
# Di app/services/document_service.py
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Ukuran chunk dalam karakter
    chunk_overlap=200,     # Overlap antar chunk
    length_function=len,
)
```

## Troubleshooting

### 1. Database Connection Error
- Pastikan PostgreSQL berjalan
- Periksa DATABASE_URL di .env
- Pastikan pgvector extension terinstall

### 2. Embedding Generation Error
- Periksa OPENAI_API_KEY jika menggunakan OpenAI
- Pastikan Ollama berjalan jika menggunakan Ollama
- Periksa koneksi internet

### 3. File Upload Error
- Pastikan file format didukung
- Periksa ukuran file (max 10MB default)
- Periksa permission folder uploads

### 4. Search Not Working
- Pastikan embeddings sudah dibuat
- Jalankan "Process Pending Embeddings" di tab Manage
- Periksa query tidak kosong

## Performance Optimization

### 1. Database
- Gunakan index pada kolom vector
- Optimize query dengan proper indexing
- Monitor query performance

### 2. Embeddings
- Gunakan batch processing untuk embeddings
- Implement caching untuk embeddings yang sering digunakan
- Monitor API rate limits

### 3. File Processing
- Implement async processing untuk file besar
- Use streaming untuk file yang sangat besar
- Implement retry mechanism

## Security Considerations

### 1. File Upload
- Validate file types
- Scan for malware
- Implement file size limits
- Sanitize file names

### 2. Database
- Use connection pooling
- Implement proper authentication
- Regular backups
- Monitor access logs

### 3. API Security
- Implement rate limiting
- Use HTTPS in production
- Validate all inputs
- Implement proper error handling

## Monitoring dan Maintenance

### 1. Health Checks
- Monitor database connection
- Check embedding service availability
- Monitor disk space for uploads

### 2. Performance Metrics
- Track embedding generation time
- Monitor search response time
- Track file processing success rate

### 3. Regular Maintenance
- Clean up old files
- Optimize database
- Update dependencies
- Monitor logs

## Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License - lihat LICENSE file untuk detail.