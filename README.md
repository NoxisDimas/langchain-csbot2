# RAG (Retrieval-Augmented Generation) System

Sistem RAG lengkap dengan fitur upload file, vector database PostgreSQL, dan interface web yang modern.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd rag-system

# Run automated setup
./run_rag_system.sh
```

### Option 2: Manual Setup

#### 1. Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ dengan extension pgvector
- OpenAI API key (opsional, bisa menggunakan Ollama)

#### 2. Database Setup
```sql
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create database
CREATE DATABASE rag_database;
```

#### 3. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env dengan konfigurasi yang sesuai
# DATABASE_URL=postgresql://username:password@localhost:5432/rag_database
# OPENAI_API_KEY=your_openai_api_key_here

# Setup database
python setup_database.py setup

# Run backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

### Option 3: Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Untuk production dengan nginx
docker-compose --profile production up -d

# Untuk development dengan Ollama
docker-compose --profile local-llm up -d
```

## 📋 Features

### ✅ Document Processing
- **Supported Formats**: PDF, TXT, Markdown, CSV, Excel, Word, JSON, XML, HTML
- **Text Extraction**: Otomatis mengekstrak teks dari berbagai format
- **Smart Chunking**: Membagi dokumen menjadi chunks optimal untuk search

### ✅ Vector Database
- **PostgreSQL + pgvector**: Database vector yang powerful dan scalable
- **Schema Management**: Otomatis membuat schema untuk setiap knowledge base
- **Embedding Generation**: Support OpenAI dan Ollama

### ✅ Knowledge Base Management
- **Multiple KBs**: Buat dan kelola multiple knowledge bases
- **CRUD Operations**: Full create, read, update, delete operations
- **Schema Isolation**: Setiap KB memiliki schema terpisah

### ✅ Search & Retrieval
- **Vector Similarity**: Pencarian berdasarkan similarity vector
- **Semantic Search**: Mencari berdasarkan makna, bukan kata kunci
- **Configurable Results**: Atur jumlah hasil pencarian

### ✅ Modern UI
- **React Interface**: Interface yang user-friendly
- **File Upload**: Drag & drop atau click to upload
- **Real-time Stats**: Monitoring progress dan statistics
- **Search Interface**: Interface pencarian yang intuitif

## 🏗️ Architecture

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

## 🔧 Configuration

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

## 📚 API Documentation

Setelah menjalankan backend, dokumentasi API tersedia di:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Key Endpoints
- `POST /api/rag/upload` - Upload dan process file
- `GET /api/rag/knowledge-bases` - List knowledge bases
- `POST /api/rag/search` - Search documents
- `GET /api/rag/stats` - System statistics
- `GET /api/rag/health` - Health check

## 🎯 Usage

### 1. Upload Documents
1. Buka http://localhost:5173
2. Pilih tab "Upload Files"
3. Pilih knowledge base
4. Upload file (PDF, TXT, CSV, dll)
5. File akan diproses otomatis

### 2. Search Documents
1. Pilih tab "Search"
2. Masukkan query pencarian
3. Klik "Search"
4. Lihat hasil dengan similarity score

### 3. Manage Knowledge Base
1. Pilih tab "Manage"
2. Buat knowledge base baru
3. Lihat dan hapus documents
4. Process pending embeddings

### 4. Monitor Statistics
1. Pilih tab "Statistics"
2. Lihat overview sistem
3. Monitor embedding progress

## 🐳 Docker Deployment

### Development
```bash
# Start semua services
docker-compose up -d

# Lihat logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production
```bash
# Start dengan nginx reverse proxy
docker-compose --profile production up -d

# Dengan SSL (setup certificates terlebih dahulu)
# Edit nginx.conf dan uncomment HTTPS section
```

### Local LLM dengan Ollama
```bash
# Start dengan Ollama untuk embeddings lokal
docker-compose --profile local-llm up -d

# Pull model
docker exec rag_ollama ollama pull llama2
```

## 🔍 Troubleshooting

### Database Issues
```bash
# Check database status
cd backend
python setup_database.py status

# Reset database
python setup_database.py setup
```

### Embedding Issues
- Periksa OPENAI_API_KEY atau OLLAMA_BASE_URL
- Pastikan koneksi internet stabil
- Check rate limits

### File Upload Issues
- Periksa format file didukung
- Pastikan ukuran file < 10MB
- Check folder permissions

### Docker Issues
```bash
# Rebuild images
docker-compose build --no-cache

# Clean up
docker-compose down -v
docker system prune -a
```

## 📊 Performance

### Optimization Tips
- Gunakan batch processing untuk embeddings
- Implement caching untuk queries yang sering
- Monitor database performance
- Use proper indexing

### Monitoring
- Health checks: http://localhost:8000/api/rag/health
- System stats: http://localhost:8000/api/rag/stats
- Database monitoring dengan pgAdmin atau similar

## 🔒 Security

### Best Practices
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Regular security updates
- Monitor access logs

### File Upload Security
- Validate file types
- Scan for malware
- Implement file size limits
- Sanitize file names

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [RAG_README.md](RAG_README.md)
- **Issues**: Create GitHub issue
- **Discussions**: Use GitHub Discussions

---

**Happy RAG-ing! 🚀**