# RAG System Project Structure

```
rag-system/
├── 📁 backend/                          # Backend API (FastAPI)
│   ├── 📁 app/
│   │   ├── 📁 api/                      # API endpoints
│   │   │   ├── chat.py                  # Chat API
│   │   │   ├── rag.py                   # RAG API endpoints
│   │   │   ├── telegram.py              # Telegram integration
│   │   │   ├── whatsapp.py              # WhatsApp integration
│   │   │   ├── crm.py                   # CRM integration
│   │   │   └── docs.py                  # Documentation API
│   │   ├── 📁 persistence/              # Database layer
│   │   │   ├── models.py                # SQLAlchemy models
│   │   │   ├── repositories.py          # Data access layer
│   │   │   └── db.py                    # Database connection
│   │   ├── 📁 services/                 # Business logic
│   │   │   ├── database_service.py      # Database management
│   │   │   ├── document_service.py      # Document processing
│   │   │   ├── embedding_service.py     # Vector embeddings
│   │   │   ├── conversation.py          # Chat conversation
│   │   │   ├── 📁 rag/                  # RAG components
│   │   │   │   ├── ingest.py            # Document ingestion
│   │   │   │   └── retriever.py         # Document retrieval
│   │   │   ├── 📁 langgraph/            # LangGraph agents
│   │   │   ├── 📁 llm/                  # LLM providers
│   │   │   ├── 📁 memory/               # Memory management
│   │   │   ├── 📁 notifications/        # Notification services
│   │   │   ├── 📁 ecommerce/            # E-commerce integrations
│   │   │   └── 📁 integrations/         # External integrations
│   │   ├── 📁 utils/                    # Utility functions
│   │   ├── 📁 tests/                    # Test files
│   │   ├── config.py                    # Configuration
│   │   └── main.py                      # FastAPI app
│   ├── requirements.txt                 # Python dependencies
│   ├── setup_database.py               # Database setup script
│   ├── test_rag_system.py              # RAG system tests
│   ├── Dockerfile                      # Backend Docker image
│   └── .dockerignore                   # Docker ignore file
│
├── 📁 frontend/                         # Frontend (React + TypeScript)
│   ├── 📁 src/
│   │   ├── 📁 ui/
│   │   │   ├── App.tsx                  # Main app component
│   │   │   └── RAGUpload.tsx            # RAG interface component
│   │   └── main.tsx                     # App entry point
│   ├── package.json                     # Node.js dependencies
│   ├── tsconfig.json                    # TypeScript config
│   ├── Dockerfile                      # Frontend Docker image
│   └── .dockerignore                   # Docker ignore file
│
├── 📄 docker-compose.yml               # Docker services orchestration
├── 📄 nginx.conf                       # Nginx reverse proxy config
├── 📄 init.sql                         # Database initialization
├── 📄 run_rag_system.sh               # Automated setup script
├── 📄 start_rag.sh                    # Quick start script
├── 📄 README.md                        # Main documentation
├── 📄 RAG_README.md                    # Detailed RAG documentation
└── 📄 PROJECT_STRUCTURE.md             # This file
```

## Key Components

### 🔧 Backend Services

#### Database Service (`database_service.py`)
- Manages PostgreSQL database connections
- Handles schema creation and management
- CRUD operations for knowledge bases and documents
- Automatic schema creation for new knowledge bases

#### Document Service (`document_service.py`)
- Processes various file formats (PDF, TXT, CSV, Excel, Word, etc.)
- Text extraction from different file types
- Document chunking for optimal vector search
- File upload and storage management

#### Embedding Service (`embedding_service.py`)
- Generates vector embeddings using OpenAI or Ollama
- Manages embedding storage in PostgreSQL with pgvector
- Vector similarity search functionality
- Batch processing for embeddings

### 🌐 API Endpoints

#### RAG API (`api/rag.py`)
- `POST /api/rag/upload` - Upload dan ingest chunks ke vectorstore
- `GET /api/rag/knowledge-bases` - List knowledge bases
- `POST /api/rag/knowledge-bases` - Create knowledge base
- `DELETE /api/rag/knowledge-bases/{name}` - Delete knowledge base
- (Legacy documents endpoints removed in RAG-only mode)
- `POST /api/rag/search` - Search documents
- `GET /api/rag/stats` - System statistics
- (Legacy process-embeddings endpoint removed)
- `GET /api/rag/health` - Health check

### 🎨 Frontend Components

#### Main App (`ui/App.tsx`)
- Navigation between Chat and RAG interfaces
- Chat functionality integration
- Responsive design

#### RAG Interface (`ui/RAGUpload.tsx`)
- File upload interface with drag & drop
- Knowledge base management
- Document search interface
- System statistics dashboard
- Tabbed interface for different functions

### 🗄️ Database Models
RAG-only: penyimpanan dokumen/embeddings dikelola oleh LangChain PGVector; model SQLAlchemy lokal untuk dokumen/embeddings telah dihapus.

#### Knowledge Base Model
```python
class KnowledgeBase(Base):
    id = Column(UUID, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
    schema_name = Column(String, unique=True)
    is_active = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

## 🚀 Deployment Options

### 1. Local Development
```bash
# Setup
./run_rag_system.sh

# Start services
./start_rag.sh
```

### 2. Docker Development
```bash
# Start all services
docker-compose up -d

# With local LLM (Ollama)
docker-compose --profile local-llm up -d
```

### 3. Production Deployment
```bash
# With nginx reverse proxy
docker-compose --profile production up -d
```

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key for embeddings
- `OLLAMA_BASE_URL` - Ollama base URL (alternative)
- `LANGSMITH_API_KEY` - LangSmith monitoring (optional)

### Database Setup
- PostgreSQL 12+ with pgvector extension
- Automatic schema creation
- Vector indexing for similarity search

## 📊 Monitoring

### Health Checks
- Backend: `http://localhost:8000/api/rag/health`
- System stats: `http://localhost:8000/api/rag/stats`
- API docs: `http://localhost:8000/docs`

### Logs
```bash
# View backend logs
./start_rag.sh logs backend

# View frontend logs
./start_rag.sh logs frontend
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
./start_rag.sh test

# Run specific test
cd backend
python test_rag_system.py --test health
```

### Test Coverage
- API endpoint testing
- Database service testing
- Document processing testing
- Embedding generation testing
- File upload testing

## 🔒 Security Features

### File Upload Security
- File type validation
- File size limits (10MB default)
- Malware scanning (can be implemented)
- Secure file storage

### API Security
- Rate limiting
- Input validation
- CORS configuration
- Error handling

### Database Security
- Connection pooling
- Prepared statements
- Schema isolation
- Access control

## 📈 Performance Optimization

### Database Optimization
- Vector indexing for similarity search
- Connection pooling
- Query optimization
- Batch processing

### Embedding Optimization
- Batch embedding generation
- Caching for frequent queries
- Rate limit management
- Async processing

### File Processing
- Streaming for large files
- Async processing
- Background tasks
- Progress tracking

## 🔄 Workflow

### Document Processing Flow
1. **Upload** - User uploads file via frontend
2. **Validation** - Check file type and size
3. **Extraction** - Extract text from file
4. **Chunking** - Split text into chunks
5. **Storage** - Store document and chunks in database
6. **Embedding** - Generate embeddings for chunks (background)
7. **Indexing** - Store embeddings in vector database

### Search Flow
1. **Query** - User enters search query
2. **Embedding** - Generate embedding for query
3. **Similarity** - Find similar chunks using vector similarity
4. **Ranking** - Rank results by similarity score
5. **Response** - Return ranked results to user

## 🛠️ Development

### Adding New File Types
1. Add file extension to `supported_extensions` in `document_service.py`
2. Implement extraction method in `DocumentService`
3. Update frontend file type validation
4. Add tests for new file type

### Adding New Embedding Models
1. Update `EmbeddingService` initialization
2. Add model configuration
3. Update environment variables
4. Test with new model

### Extending API
1. Add new endpoints in `api/rag.py`
2. Update Pydantic models
3. Add service methods
4. Update frontend interface
5. Add tests

## 📚 Documentation

- **Main README**: Overview and quick start
- **RAG README**: Detailed RAG system documentation
- **API Docs**: Auto-generated from FastAPI
- **Project Structure**: This file
- **Docker Docs**: Container deployment guide