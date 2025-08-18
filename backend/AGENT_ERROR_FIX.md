# Agent OutputParserException Fix

## Masalah

Error `OutputParserException` terjadi pada sistem RAG ketika LLM mengembalikan output yang tidak sesuai dengan format yang diharapkan oleh ReAct agent parser. Error ini muncul dengan pesan:

```
OutputParserException('Could not parse LLM output: `Question: What is the meaning of halo in English?
Thought: I need to translate "halo" to English.
Action: translate_to_english, Input: halo`')
```

## Penyebab

1. **Format Output Tidak Sesuai**: LLM mengembalikan output yang tidak mengikuti format ReAct yang tepat
2. **Prompt Template Kurang Jelas**: Instruksi format tidak cukup eksplisit untuk LLM
3. **Masalah Parsing**: Parser tidak dapat menangani variasi format output dari LLM
4. **Kurangnya Error Handling**: Tidak ada fallback mechanism ketika parsing gagal

## Solusi yang Diimplementasikan

### 1. Perbaikan Prompt Template (`agent_react.py`)

- **Format yang Lebih Eksplisit**: Menambahkan instruksi yang lebih jelas tentang format yang diharapkan
- **Aturan Kritis**: Menambahkan aturan format yang lebih ketat
- **Peringatan Khusus**: Memberikan peringatan tentang penggunaan koma dan line breaks

```python
CRITICAL FORMATTING RULES:
- You MUST follow the EXACT format below
- Use EXACTLY one tool per Action step
- NEVER combine multiple actions in one step
- ALWAYS use the exact format with proper line breaks
- NEVER use commas in Action Input - use separate lines
```

### 2. Error Handling yang Lebih Baik (`nodes.py`)

- **OutputParserException Handling**: Menangani error parsing secara spesifik
- **Fallback Responses**: Memberikan respons fallback yang kontekstual
- **Agent Creation Validation**: Memvalidasi pembuatan agent sebelum digunakan

### 3. Utility Functions (`agent_utils.py`)

- **Context-Aware Fallbacks**: Respons fallback berdasarkan jenis agent dan query
- **Error Logging**: Logging yang lebih detail untuk debugging
- **Input Sanitization**: Membersihkan input sebelum diproses

### 4. Fallback Mechanism

Sistem sekarang memiliki fallback responses yang cerdas:

- **General QA**: Respons untuk greeting, thanks, dll
- **Order Status**: Respons khusus untuk pertanyaan status pesanan
- **Product Recommendation**: Respons untuk rekomendasi produk
- **Handover**: Respons untuk handover ke human agent

## Implementasi

### File yang Dimodifikasi:

1. `backend/app/services/langgraph/agent_react.py`
   - Perbaikan prompt template
   - Penambahan fallback mechanism
   - Validasi agent creation

2. `backend/app/services/langgraph/nodes.py`
   - Error handling yang lebih baik
   - Penggunaan utility functions
   - Input sanitization

3. `backend/app/utils/agent_utils.py` (Baru)
   - Utility functions untuk error handling
   - Context-aware fallback responses
   - Input validation dan sanitization

## Testing

Untuk menguji perbaikan:

1. **Test dengan Query Sederhana**:
   ```bash
   curl -X POST "http://localhost:8000/api/chat" \
        -H "Content-Type: application/json" \
        -d '{"session_id": "test", "message": "halo", "channel": "web"}'
   ```

2. **Test dengan Query Kompleks**:
   ```bash
   curl -X POST "http://localhost:8000/api/chat" \
        -H "Content-Type: application/json" \
        -d '{"session_id": "test", "message": "Apa arti halo dalam bahasa Inggris?", "channel": "web"}'
   ```

## Monitoring

- **Logs**: Periksa logs untuk melihat error details
- **Fallback Usage**: Monitor penggunaan fallback responses
- **Agent Performance**: Track agent creation success rate

## Best Practices

1. **Prompt Engineering**: Gunakan prompt yang jelas dan eksplisit
2. **Error Handling**: Selalu implementasikan fallback mechanisms
3. **Input Validation**: Sanitasi input sebelum processing
4. **Logging**: Log error details untuk debugging
5. **Testing**: Test dengan berbagai jenis input

## Troubleshooting

Jika masih mengalami error:

1. **Periksa Logs**: Lihat detail error di logs
2. **Validasi Input**: Pastikan input tidak terlalu panjang atau mengandung karakter khusus
3. **Model Configuration**: Periksa konfigurasi LLM model
4. **Fallback Response**: Pastikan fallback mechanism berfungsi

## Kesimpulan

Perbaikan ini mengatasi masalah `OutputParserException` dengan:
- Prompt template yang lebih robust
- Error handling yang komprehensif
- Fallback mechanism yang cerdas
- Input validation dan sanitization

Sistem sekarang lebih tahan terhadap error parsing dan memberikan pengalaman pengguna yang lebih baik.