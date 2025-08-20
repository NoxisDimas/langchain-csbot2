# RAG System Consistency Guide

## Overview

Dokumen ini menjelaskan bagaimana memastikan konsistensi antara penyimpanan dan retrieval data dalam sistem RAG (Retrieval Augmented Generation).

## 🔍 **Analisis Konsistensi**

### **Komponen yang Menggunakan Collection `ai_cs` (DB_SCHEMA):**

1. **RAG Retriever** (`app/services/rag/retriever.py`)
   - Menggunakan `collection_name=f"{_settings.DB_SCHEMA}"`
   - Digunakan oleh `retrieve_knowledge()` function

2. **API Upload** (`app/api/rag.py`)
   - Menggunakan `collection_name=settings.DB_SCHEMA` saat upload
   - Menggunakan `collection_name=settings.DB_SCHEMA` saat search

3. **VectorStoreService** (`app/services/vectorstore_service.py`)
   - Mendukung parameter `collection_name` untuk semua operasi
   - Default collection: `"documents"` (hanya jika tidak di-specify)

4. **Tools** (`app/services/langgraph/tools.py`)
   - `retrieve_kb_snippets_tool()` menggunakan `retrieve_knowledge()`
   - Otomatis menggunakan collection yang sama dengan RAG retriever

### **Komponen yang Menggunakan Collection Terpisah:**

1. **Memory Service** (`app/services/memory/vector_memory.py`)
   - Menggunakan `collection_name=f"{_settings.DB_SCHEMA}_memory"`
   - Terpisah dari knowledge base untuk isolasi data

## ✅ **Verifikasi Konsistensi**

### **Test yang Dilakukan:**

```bash
python3 test_consistency.py
```

**Hasil yang Diharapkan:**
- ✅ Storage via VectorStoreService → collection `ai_cs`
- ✅ Retrieval via RAG retriever → collection `ai_cs`
- ✅ Retrieval via VectorStoreService search → collection `ai_cs`
- ✅ Tool integration → collection `ai_cs`
- ✅ Content consistency → data yang sama ditemukan di semua retrieval

### **Database Verification:**

```sql
-- Check collection stats
SELECT c.name as collection_name, COUNT(e.id) as doc_count 
FROM langchain_pg_collection c 
LEFT JOIN langchain_pg_embedding e ON c.uuid = e.collection_id 
GROUP BY c.uuid, c.name 
ORDER BY c.name;
```

**Expected Output:**
```
 collection_name | doc_count 
-----------------+-----------
 ai_cs           |         X
 ai_cs_memory    |         Y
 documents       |         Z
```

## 🛠️ **Best Practices**

### **1. Selalu Gunakan DB_SCHEMA untuk Knowledge Base**

```python
# ✅ Correct
ids = vector_service.add_documents(chunks, collection_name=settings.DB_SCHEMA)
docs = vector_service.search(query, collection_name=settings.DB_SCHEMA)

# ❌ Avoid
ids = vector_service.add_documents(chunks)  # Uses default "documents"
```

### **2. Konsisten dalam API Endpoints**

```python
# ✅ Correct - API upload
ids = vector_service.add_documents(chunks, collection_name=settings.DB_SCHEMA)

# ✅ Correct - API search  
docs = vector_service.search(query, collection_name=settings.DB_SCHEMA)
```

### **3. Gunakan RAG Retriever untuk Tools**

```python
# ✅ Correct - Tool menggunakan RAG retriever
@tool("retrieve_kb_snippets", return_direct=False)
def retrieve_kb_snippets_tool(query: str) -> Dict[str, Any]:
    docs = retrieve_knowledge(query)  # Otomatis menggunakan DB_SCHEMA
    return {"snippets": [d.page_content for d in docs[:5]]}
```

## 🔧 **Troubleshooting**

### **Problem: Data tidak ditemukan saat retrieval**

**Possible Causes:**
1. Data disimpan di collection yang berbeda
2. DB_SCHEMA tidak konsisten
3. Embedding model berbeda

**Solutions:**
1. Check collection stats di database
2. Verify DB_SCHEMA setting
3. Ensure embedding model consistency

### **Problem: Warning deprecation**

**Solutions:**
1. Use `retriever.invoke()` instead of `retriever.get_relevant_documents()`
2. Use `tool.invoke()` instead of `tool()`

## 📋 **Checklist Konsistensi**

- [ ] RAG retriever menggunakan `DB_SCHEMA`
- [ ] API upload menggunakan `DB_SCHEMA`
- [ ] API search menggunakan `DB_SCHEMA`
- [ ] Tools menggunakan RAG retriever
- [ ] Memory service menggunakan collection terpisah
- [ ] No deprecation warnings
- [ ] Test consistency passes

## 🎯 **Kesimpulan**

Sistem RAG sekarang sudah konsisten dengan:
- **Single source of truth**: Semua komponen menggunakan collection `ai_cs` (DB_SCHEMA)
- **Proper separation**: Memory menggunakan collection terpisah
- **Consistent API**: Upload dan search menggunakan collection yang sama
- **Tool integration**: Tools menggunakan RAG retriever yang konsisten

Semua komponen sekarang dapat memberikan data yang diminta oleh agent dengan konsisten.