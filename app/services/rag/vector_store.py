from dotenv import load_dotenv
import os
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector
from app.services.llm.provider import get_embedding_model
from app.config import get_settings
from app.services.rag.loader import Loader

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

settings = get_settings()

class VectorStore:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = os.path.join(self.BASE_DIR, "..", "..", "..", "uploads")
        
        # Get embedding model from provider
        self.model = get_embedding_model()
        
        # Database configuration
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set.")
        self.CONNECTION_STRING = settings.DATABASE_URL
        self.COLLECTION_NAME = settings.DB_SCHEMA
        
        self.file_paths = []
        self.all_docs = []
        
        # Initialize PGVector store
        self.store = PGVector(
            embeddings=self.model,
            collection_name=self.COLLECTION_NAME,
            connection=self.CONNECTION_STRING,
            use_jsonb=True
        )
        
        # Text splitter configuration
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False
        )

    def check_data_folder(self):
        """Check if uploads folder exists and get all file paths"""
        if not os.path.isdir(self.data_folder):
            logging.warning(f"Uploads folder not found: {self.data_folder}")
            os.makedirs(self.data_folder, exist_ok=True)
            logging.info(f"Created uploads folder: {self.data_folder}")
            return []
        
        self.file_paths = [
            os.path.join(self.data_folder, f)
            for f in os.listdir(self.data_folder)
            if os.path.isfile(os.path.join(self.data_folder, f))
        ]
        logging.info(f"Found {len(self.file_paths)} files in uploads folder")
        return self.file_paths

    def load_by_type_data(self, file):
        """Load document based on file type"""
        ext = file.split(".")[-1].lower()
        file_name = os.path.basename(file)
        title = file_name.replace(f".{ext}", "").replace("-", " ").title()

        if ext in ["txt", "csv", "pdf", "docx", "xlsx", "md"]:
            return Loader(file_path=file, title=title, category=f"{ext} file")
        else:
            logging.warning(f"[Load by type] Unsupported file extension: {ext}")
            return None

    def build_vector_store(self, update_existing=True):
        """Build vector store from documents in uploads folder"""
        logging.info("🔧 Starting document ingestion...")

        if not self.CONNECTION_STRING or not self.COLLECTION_NAME:
            raise ValueError("[Build Vector] DATABASE_URL or DB_SCHEMA not found in environment")

        self.check_data_folder()

        if not self.file_paths:
            logging.warning("[Build Vector] No files found in uploads folder.")
            return None

        for file in self.file_paths:
            loader = self.load_by_type_data(file)
            if loader:
                try:
                    docs = loader.auto_loader()
                    self.all_docs.extend(docs)
                    logging.info(f"✅ Loaded {len(docs)} documents from {os.path.basename(file)}")
                except Exception as e:
                    logging.error(f"[Build_Vector] ❌ Failed loading {file}: {e}")

        if not self.all_docs:
            logging.warning("[Build_Vector] No documents loaded.")
            return None

        logging.info(f"📚 Raw documents: {len(self.all_docs)}")
        splitted_docs = self.text_splitter.split_documents(self.all_docs)
        logging.info(f"📄 Split documents: {len(splitted_docs)}")

        # Create collection
        try:
            self.store.create_collection()
            logging.info("✅ Collection ensured in PostgreSQL.")
        except Exception as e:
            logging.warning(f"Collection creation warning: {e}")

        if update_existing:
            self._remove_existing_titles(splitted_docs)

        # Add documents to vector store
        try:
            self.store.add_documents(splitted_docs)
            logging.info(f"📦 Documents added to vector store: {len(splitted_docs)}")
        except Exception as e:
            logging.error(f"Failed to add documents to vector store: {e}")
            raise

        return self.store

    def _remove_existing_titles(self, docs):
        """Remove existing documents with same titles"""
        unique_titles = set([doc.metadata.get("title") for doc in docs])
        logging.info(f"🔁 Removing existing docs with titles: {unique_titles}")
        
        for title in unique_titles:
            try:
                self.store.delete(filter={"title": {"equals": title}})
                logging.info(f"🗑️ Removed existing documents with title: {title}")
            except Exception as e:
                logging.warning(f"Failed to remove existing documents with title {title}: {e}")

    def get_vector_store(self):
        """Get the vector store instance"""
        if not self.CONNECTION_STRING or not self.COLLECTION_NAME:
            raise ValueError("[Get Vector Store] Missing DATABASE_URL or DB_SCHEMA")
        return self.store

    def filter_by_metadata(self, key, value, k=100, offset=0):
        """
        Filter documents from vector store based on metadata.
        key: "category", "title", "source"
        value: string to search for
        k: maximum number of results to return (default 100)
        offset: number of results to skip for pagination (default 0)
        """
        if key not in ["category", "title", "source"]:
            raise ValueError("[Filter by Metadata] Only 'category', 'title', or 'source' are supported as filters.")
        
        try:
            results = self.store.similarity_search_with_score(
                query="", k=k, filter={key: {"$eq": value}}, offset=offset
            )
            logging.info(f"🔍 Found {len(results)} documents with {key}={value}")
            return results
        except Exception as e:
            logging.error(f"Failed to filter by metadata {key}={value}: {e}")
            return []

    def similarity_search(self, query, k=5, filter_dict=None):
        """
        Perform similarity search with optional filtering
        """
        try:
            if filter_dict:
                results = self.store.similarity_search_with_score(
                    query=query, k=k, filter=filter_dict
                )
            else:
                results = self.store.similarity_search_with_score(query=query, k=k)
            
            logging.info(f"🔍 Similarity search returned {len(results)} results for query: {query[:50]}...")
            return results
        except Exception as e:
            logging.error(f"Failed to perform similarity search: {e}")
            return []

    def get_collection_stats(self):
        """Get statistics about the vector store collection"""
        try:
            # This is a simple implementation - you might want to enhance it
            # based on your specific needs
            return {
                "collection_name": self.COLLECTION_NAME,
                "database_url": self.CONNECTION_STRING.split("@")[-1] if "@" in self.CONNECTION_STRING else "configured",
                "embedding_model": str(self.model),
                "uploads_folder": self.data_folder,
                "files_count": len(self.file_paths)
            }
        except Exception as e:
            logging.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}