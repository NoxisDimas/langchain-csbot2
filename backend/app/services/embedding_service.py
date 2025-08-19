import os
import json
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from app.services.database_service import DatabaseService
from app.persistence.models import DocumentEmbedding, Document
from app.config import get_settings

settings = get_settings()

class EmbeddingService:
    """Legacy embedding service removed in favor of LangChain PGVector vectorstore."""
    def __init__(self):
        raise RuntimeError("Legacy EmbeddingService is deprecated. Use VectorStoreService instead.")