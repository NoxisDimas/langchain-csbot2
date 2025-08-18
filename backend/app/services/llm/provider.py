from typing import Optional
from app.config import get_settings

from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # type: ignore
from langchain_community.chat_models import ChatOllama  # type: ignore
from langchain_community.embeddings import OllamaEmbeddings  # type: ignore


_settings = get_settings()


def get_chat_model(temperature: float = 0.2):
	"""Return a chat model: OpenAI if OPENAI_API_KEY exists, else Ollama (default)."""
	if _settings.OPENAI_API_KEY:
		return ChatOpenAI(model=_settings.OPENAI_MODEL, temperature=temperature)
	return ChatOllama(base_url=_settings.OLLAMA_BASE_URL, model=_settings.OLLAMA_MODEL, temperature=temperature)


def get_embedding_model():
	"""Return embedding model aligned with selected provider."""
	if _settings.OPENAI_API_KEY:
		return OpenAIEmbeddings()
	return OllamaEmbeddings(base_url=_settings.OLLAMA_BASE_URL, model=_settings.OLLAMA_EMBED_MODEL)