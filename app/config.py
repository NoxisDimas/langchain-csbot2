import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

	# LLM
	OPENAI_API_KEY: Optional[str] = None
	OPENAI_MODEL: str = "gpt-4o-mini"
	OLLAMA_BASE_URL: str = "http://localhost:11434"
	OLLAMA_MODEL: str = "llama3.1:8b-instruct"
	OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
	GROQ_API_KEY: Optional[str] = None

	# DB
	DATABASE_URL: Optional[str] = None
	DB_SCHEMA: str = "ai_cs"

	# LangSmith
	LANGSMITH_API_KEY: Optional[str] = None
	LANGSMITH_PROJECT: str = "ai-cs"
	LANGCHAIN_TRACING_V2: bool = True

	# Telegram
	TELEGRAM_BOT_TOKEN: Optional[str] = None
	TELEGRAM_SUPPORT_CHAT_ID: Optional[str] = None

	# WhatsApp Business (optional)
	WA_TOKEN: Optional[str] = None
	WA_PHONE_ID: Optional[str] = None

	# CRM (optional)
	CRM_BASE_URL: Optional[str] = None
	CRM_API_KEY: Optional[str] = None

	# Email
	SMTP_HOST: Optional[str] = None
	SMTP_PORT: int = 587
	SMTP_USER: Optional[str] = None
	SMTP_PASSWORD: Optional[str] = None
	SUPPORT_EMAIL_TO: Optional[str] = None
	SUPPORT_EMAIL_FROM: str = "no-reply@example.com"

	# Ecommerce: Shopify (optional)
	SHOPIFY_STORE_DOMAIN: Optional[str] = None  # e.g., mystore.myshopify.com
	SHOPIFY_ACCESS_TOKEN: Optional[str] = None

	# Ecommerce: WooCommerce (optional)
	WOO_BASE_URL: Optional[str] = None  # e.g., https://example.com
	WOO_CONSUMER_KEY: Optional[str] = None
	WOO_CONSUMER_SECRET: Optional[str] = None

	# Ecommerce: Shopee (optional)
	SHOPEE_PARTNER_ID: Optional[str] = None
	SHOPEE_PARTNER_KEY: Optional[str] = None
	SHOPEE_SHOP_ID: Optional[str] = None
	SHOPEE_BASE_URL: Optional[str] = None  # default open api base if provided

	# Ecommerce: Tokopedia (optional)
	TOKO_CLIENT_ID: Optional[str] = None
	TOKO_CLIENT_SECRET: Optional[str] = None
	TOKO_MERCHANT_ID: Optional[str] = None
	TOKO_BASE_URL: Optional[str] = None

	# Policy
	DATA_RETENTION_DAYS: int = 60
	SENSITIVE_TTL_HOURS: int = 1
	DEFAULT_LOCALE: str = "id"


def get_settings() -> Settings:
	return Settings()  # reads .env automatically