import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.chat import router as chat_router
from app.api.telegram import router as telegram_router
from app.api.docs import router as docs_router
from app.api.whatsapp import router as whatsapp_router
from app.api.crm import router as crm_router
from app.api.rag import router as rag_router
from app.persistence.db import init_db


settings = get_settings()

# Propagate LangSmith envs if provided
if settings.LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY or ""
os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
os.environ["LANGCHAIN_TRACING_V2"] = "true" if settings.LANGCHAIN_TRACING_V2 else "false"


# === Lifespan handler ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    try:
        if settings.DATABASE_URL:
            init_db()
            print("✅ Database initialized")
    except Exception as e:
            print(f"⚠️ Failed to init DB: {e}")

    yield

    # --- Shutdown ---
    print("🛑 App shutting down...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="AI Customer Service",
    version="0.1.0",
    lifespan=lifespan
)


# Enable CORS for local frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
def health():
    return {"status": "ok"}


# Register routers
app.include_router(chat_router, prefix="/api")
app.include_router(telegram_router, prefix="/api/telegram")
app.include_router(docs_router, prefix="/api/docs")
app.include_router(whatsapp_router, prefix="/api/whatsapp")
app.include_router(crm_router, prefix="/api/crm")
app.include_router(rag_router, prefix="/api")
