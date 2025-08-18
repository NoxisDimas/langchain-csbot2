from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Boolean, JSON, Float
from datetime import datetime, timedelta
from typing import Optional
from app.config import get_settings
from sqlalchemy.dialects.postgresql import UUID
import uuid


settings = get_settings()


class Base(DeclarativeBase):
	pass


class Conversation(Base):
	__tablename__ = f"{settings.DB_SCHEMA}_conversation"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	session_id: Mapped[str] = mapped_column(String(255), index=True, unique=True)
	channel: Mapped[str] = mapped_column(String(50))
	locale: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
	user_profile: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

	messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
	__tablename__ = f"{settings.DB_SCHEMA}_message"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	conversation_id: Mapped[int] = mapped_column(ForeignKey(f"{Conversation.__tablename__}.id", ondelete="CASCADE"))
	role: Mapped[str] = mapped_column(String(20))  # user/assistant/system
	content: Mapped[str] = mapped_column(Text)
	pii_redactions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")


class SensitiveData(Base):
	__tablename__ = f"{settings.DB_SCHEMA}_sensitive"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	conversation_id: Mapped[int] = mapped_column(ForeignKey(f"{Conversation.__tablename__}.id", ondelete="CASCADE"))
	data: Mapped[dict] = mapped_column(JSON)
	expires_at: Mapped[datetime] = mapped_column(DateTime)
	created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

	@staticmethod
	def ttl_from_now(hours: int) -> datetime:
		return datetime.utcnow() + timedelta(hours=hours)


class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string - renamed from metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationship with embeddings
    embeddings: Mapped[list["DocumentEmbedding"]] = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[float] = mapped_column("embedding", Float, nullable=False)  # This will be a vector column
    embedding_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string - renamed from metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship with document
    document: Mapped[Document] = relationship("Document", back_populates="embeddings")


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    schema_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)