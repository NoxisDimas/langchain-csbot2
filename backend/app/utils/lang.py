from langdetect import detect
from typing import Optional
from functools import lru_cache
import logging


SUPPORTED_LANGS = {"id", "en"}
logging.basicConfig(level=logging.INFO)


def detect_language(text: str) -> Optional[str]:
	try:
		lang = detect(text)
		if lang in SUPPORTED_LANGS:
			return lang
		# default to English if unknown
		return "en"
	except Exception as e:
		logging.error(f"Error in translating text: {e}")
		return "en"


@lru_cache(maxsize=5)
def _get_translator_model():
	# Lazy import to avoid heavy import at module load time
	from app.services.llm.provider import get_chat_model
	return get_chat_model(temperature=0.0)


def translate_text(text: str, target_lang: str) -> str:
	if not text:
		return text
	# Simple LLM-based translation
	model = _get_translator_model()
	system = (
		"You are a professional translator. Translate the user text to the target language with the same meaning and tone."
		" Only return the translated text."
	)
	prompt = f"Target language: {target_lang}.\nText: {text}"
	try:
		resp = model.invoke([{"role": "system", "content": system}, {"role": "user", "content": prompt}])
		return getattr(resp, "content", str(resp))
	except Exception:
		return text


def translate_to_language(text: str, target_lang: str) -> str:
	# If already in target language, return as is
	try:
		src = detect_language(text)
		if src == target_lang:
			return text
		return translate_text(text, target_lang)
	except Exception:
		return text