from typing import Optional
from app.config import get_settings

from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # type: ignore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_groq import ChatGroq


_settings = get_settings()


def get_chat_model(temperature: float = 0.2):
	"""Return a chat model: OpenAI if OPENAI_API_KEY exists, else Ollama (default)."""
	if _settings.OPENAI_API_KEY and _settings.OPENAI_API_KEY.strip():
		return ChatOpenAI(model=_settings.OPENAI_MODEL, temperature=temperature)
	elif _settings.GROQ_API_KEY and _settings.GROQ_API_KEY.strip():
		return ChatGroq(
				api_key=_settings.GROQ_API_KEY,
				model="moonshotai/kimi-k2-instruct",
				temperature=0,
				max_tokens=None,
				timeout=None,
				max_retries=2)
	return ChatOllama(base_url=_settings.OLLAMA_BASE_URL, model=_settings.OLLAMA_MODEL, temperature=temperature)


def get_embedding_model():
	"""Return embedding model aligned with selected provider."""
	if _settings.OPENAI_API_KEY and _settings.OPENAI_API_KEY.strip():
		return OpenAIEmbeddings()
	if _settings.OLLAMA_BASE_URL:
		return OllamaEmbeddings(base_url=_settings.OLLAMA_BASE_URL, model=_settings.OLLAMA_EMBED_MODEL)
	raise RuntimeError("No embedding provider configured. Set OPENAI_API_KEY or OLLAMA_BASE_URL")