from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.persistence.models import Base


settings = get_settings()
_engine = None
_SessionLocal = None


def init_db():
	global _engine, _SessionLocal
	if not settings.DATABASE_URL:
		raise RuntimeError("DATABASE_URL is not configured")
	_engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
	_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
	with _engine.connect() as conn:
		# Ensure pgvector extension and schema
		conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
		conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA}"))
		conn.commit()
	# Create tables
	Base.metadata.create_all(bind=_engine)


def get_db() -> Generator:
	if _SessionLocal is None:
		raise RuntimeError("DB not initialized. Call init_db() on startup.")
	db = _SessionLocal()
	try:
		yield db
	finally:
		db.close()