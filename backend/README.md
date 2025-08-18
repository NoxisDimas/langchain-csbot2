# AI Customer Service (Python + LangChain + LangGraph)

Backend: FastAPI (Python). Frontend: React (testing widget). Multi-channel: Web + Telegram (+ optional WhatsApp). RAG + Memory via Postgres (pgvector). LLM fallback: OpenAI if `OPENAI_API_KEY` is set, otherwise self-hosted Ollama by default.

## Highlights
- LangGraph orchestration: Start → Router → (Order_Status | Product_Recommendation | General_QA | Handover) → End
- ReAct Agents per node (LangChain `create_react_agent`) with at least two tools each
- RAG + Memory backed by PGVector (optional; DB-less mode still works)
- Multi-channel: Web, Telegram, optional WhatsApp; consistent conversation state
- Optional E-commerce adapters: Shopify, WooCommerce, Shopee, Tokopedia (auto-fallback to Mock)
- Handover to human via Email/Telegram; optional CRM ticket API
- Compliance hooks: consent, region check, PII deletion request
- Observability: LangSmith (optional)

## Architecture
- API (FastAPI): `app/api/*`
  - Web chat endpoint: `POST /api/chat`
  - Telegram webhook: `POST /api/telegram/webhook`
  - WhatsApp webhook (optional): `POST /api/whatsapp/webhook`
  - CRM ticket (optional): `POST /api/crm/ticket`
  - Docs overview: `GET /api/docs/design`
- Services (LangGraph, Agents, RAG, Tools): `app/services/*`
  - LangGraph state/nodes/graph: `services/langgraph/{state,nodes,graph}.py`
  - ReAct agents per node: `services/langgraph/agent_react.py`
  - Tools: `services/langgraph/tools.py`
  - LLM provider (OpenAI/Ollama fallback): `services/llm/provider.py`
  - RAG vector store: `services/rag/{retriever,ingest}.py`
  - Vector memory: `services/memory/vector_memory.py`
- Persistence (SQLAlchemy): `app/persistence/*`
  - Models: `models.py`, Repositories: `repositories.py`, DB init: `db.py`
- Utilities: `app/utils/*` (language detect/translate, PII masking, sentiment)
- E-commerce adapters: `app/services/ecommerce/*` with registry chooser

## State (TypedDict)
`GraphState` fields:
- conversation_history: list of `{type: human|ai|system, content}`
- user_query, current_task, assistant_response
- user_profile, knowledge_refs
- sentiment_score, handoff_to_human
- locale, detected_language, pii_redactions
- order_id

## ReAct Agents per Node
- Order_Status: tools `extract_order_id`, `get_order_status`, `analyze_sentiment`
- Product_Recommendation: tools `search_products`, `retrieve_memory`
- General_QA: tools `translate_to_english`, `retrieve_kb_snippets`
- Handover: tools `notify_email_support`, `notify_telegram_support`

## E-commerce Adapters (Optional)
Adapter aktif ditentukan otomatis berdasarkan variabel environment (urutan prioritas):
1. Shopify (`SHOPIFY_STORE_DOMAIN`, `SHOPIFY_ACCESS_TOKEN`)
2. WooCommerce (`WOO_BASE_URL`, `WOO_CONSUMER_KEY`, `WOO_CONSUMER_SECRET`)
3. Shopee (`SHOPEE_PARTNER_ID`, `SHOPEE_PARTNER_KEY`, `SHOPEE_SHOP_ID`, `SHOPEE_BASE_URL`) – stub aman
4. Tokopedia (`TOKO_CLIENT_ID`, `TOKO_CLIENT_SECRET`, `TOKO_MERCHANT_ID`, `TOKO_BASE_URL`) – stub aman
5. Mock (default)

## Multi-channel
- Web widget (React): call `POST /api/chat` with `{ session_id, message, channel }`
- Telegram: set webhook ke `/api/telegram/webhook`
- WhatsApp (opsional): set webhook ke `/api/whatsapp/webhook` jika `WA_TOKEN` dan `WA_PHONE_ID` tersedia

## Compliance
- Consent: header `X-User-Consent` harus true/yes/1 (default true); gunakan dependency `require_consent`
- Region check: hook `region_check` untuk residency (placeholder)
- PII deletion: `request_pii_deletion(user_id)` untuk workflow penghapusan
- Retention & TTL: dikontrol oleh env `DATA_RETENTION_DAYS`, `SENSITIVE_TTL_HOURS`

## Setup
1) Prerequisites
- Python 3.11+
- Postgres 15+ dengan `pgvector`
- Optional: Ollama (`ollama serve`) dengan model yang dibutuhkan

2) Install
```bash
cd backend
cp .env.example .env
# edit .env sesuai kebutuhan
pip install -r requirements.txt --break-system-packages
```

3) Database
- Pastikan `DATABASE_URL` mengarah ke instance Postgres dan `CREATE EXTENSION IF NOT EXISTS vector` diizinkan.
- Aplikasi akan membuat schema dan tabel otomatis saat startup.

4) Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5) Frontend (Testing Widget)
```bash
cd ../frontend
npm i && npm run dev
```

## Environment Variables
Lihat `.env.example` untuk daftar lengkap. Penting:
- LLM: `OPENAI_API_KEY` (opsional), `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_EMBED_MODEL`
- DB: `DATABASE_URL`, `DB_SCHEMA`
- Channels: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_SUPPORT_CHAT_ID`, `WA_TOKEN`, `WA_PHONE_ID`
- E-commerce: Shopify/Woo/Shopee/Tokopedia vars (opsional)
- CRM: `CRM_BASE_URL`, `CRM_API_KEY`
- Email: `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SUPPORT_EMAIL_TO`

## Testing & Debugging
- Unit tests:
```bash
cd backend
python3 -m pytest -q
```
- Health check: GET `/health`
- Design overview: GET `/api/docs/design`

## Development Notes
- Bahasa default interaksi ke user: Indonesia; deteksi bahasa otomatis; query RAG dalam bahasa Inggris.
- Jawaban akan diterjemahkan ke bahasa user (LLM-based translation sederhana, bisa diganti layanan eksternal).
- Observabilitas LangSmith opsional. Jika tidak ada API key, warning aman diabaikan.

## Extending
- Tambah node baru: buat tools di `tools.py`, ReAct agent di `agent_react.py`, node handler di `nodes.py`, dan wiring di `graph.py`.
- Tambah channel baru: buat router di `app/api/{channel}.py`, panggil `run_conversation` dengan `session_id` unik.
- Tambah adapter e-commerce: implement `OrderStatus`/`ProductCatalog` dan daftarkan di `ecommerce/registry.py`.

## Security & Compliance
- PII masking sederhana (regex) sebelum penyimpanan.
- TTL untuk data sensitif diterapkan via model `SensitiveData`.
- Pastikan kepatuhan GDPR/CCPA/PDPA sesuai wilayah operasional, perkuat kebijakan consent dan penghapusan data.