# Agent OutputParserException Fix - Testing Guide

## Overview

Dokumen ini menjelaskan cara menguji perbaikan untuk error `OutputParserException` yang telah diimplementasikan pada sistem RAG.

## Prerequisites

1. **Backend Running**: Pastikan backend server berjalan di `http://localhost:8000`
2. **Dependencies**: Semua dependencies terinstall
3. **Environment**: File `.env` dikonfigurasi dengan benar

## Quick Test

### 1. Test Manual dengan curl

```bash
# Test greeting sederhana
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test", "message": "halo", "channel": "web"}'

# Test query yang sebelumnya error
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "test", "message": "Apa arti halo dalam bahasa Inggris?", "channel": "web"}'
```

### 2. Test dengan Script Otomatis

```bash
# Run semua test
cd backend
python test_agent_fix.py

# Run test spesifik
python test_agent_fix.py --test greeting
python test_agent_fix.py --test complex
python test_agent_fix.py --test order
python test_agent_fix.py --test product
python test_agent_fix.py --test edge
python test_agent_fix.py --test flow

# Test dengan base URL berbeda
python test_agent_fix.py --base-url "http://localhost:8001"
```

## Expected Results

### ✅ Success Cases

1. **Simple Greeting**: 
   - Input: "halo"
   - Expected: "Halo! Ada yang bisa saya bantu hari ini?"

2. **Complex Query**:
   - Input: "Apa arti halo dalam bahasa Inggris?"
   - Expected: Response yang menggunakan translate_to_english tool atau fallback response

3. **Order Status**:
   - Input: "Bagaimana status pesanan saya?"
   - Expected: Response yang menggunakan order status tools atau fallback

4. **Product Recommendation**:
   - Input: "Saya mencari laptop untuk gaming"
   - Expected: Response yang menggunakan product search tools atau fallback

### ❌ Error Cases (Should be Handled)

1. **Empty Message**: Should return fallback response
2. **Very Long Message**: Should be sanitized and processed
3. **Mixed Language**: Should handle gracefully
4. **Special Characters**: Should be sanitized

## Monitoring

### 1. Check Logs

```bash
# View backend logs
tail -f logs/backend.log

# View specific error logs
grep "OutputParserException" logs/backend.log
grep "Parsing error" logs/backend.log
```

### 2. Check API Health

```bash
# Health check
curl http://localhost:8000/api/rag/health

# System stats
curl http://localhost:8000/api/rag/stats
```

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   ```bash
   # Check if backend is running
   ps aux | grep uvicorn
   
   # Start backend if needed
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Import Errors**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Check Python path
   python -c "import sys; print(sys.path)"
   ```

3. **Environment Issues**:
   ```bash
   # Check environment variables
   cat .env
   
   # Test configuration
   python -c "from app.config import get_settings; print(get_settings())"
   ```

### Debug Mode

Untuk debugging lebih detail, tambahkan logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Testing

### Load Testing

```bash
# Test dengan multiple requests
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/chat" \
       -H "Content-Type: application/json" \
       -d "{\"session_id\": \"test_$i\", \"message\": \"halo\", \"channel\": \"web\"}" &
done
wait
```

### Memory Usage

```bash
# Monitor memory usage
watch -n 1 'ps aux | grep python | grep uvicorn'
```

## Validation Checklist

- [ ] Simple greeting works without error
- [ ] Complex queries are handled gracefully
- [ ] Fallback responses are context-aware
- [ ] Error logging is detailed
- [ ] Input sanitization works
- [ ] Agent creation is validated
- [ ] Conversation flow is maintained
- [ ] Edge cases are handled

## Reporting

Setelah menjalankan test, buat report dengan format:

```markdown
# Test Report - Agent Fix

## Date: [YYYY-MM-DD]
## Environment: [Development/Production]
## Backend Version: [Version]

## Test Results:
- Simple Greeting: ✅/❌
- Complex Query: ✅/❌
- Order Status: ✅/❌
- Product Recommendation: ✅/❌
- Edge Cases: ✅/❌
- Conversation Flow: ✅/❌

## Issues Found:
- [List any issues]

## Recommendations:
- [List recommendations]
```

## Support

Jika mengalami masalah:

1. Check logs untuk error details
2. Verify environment configuration
3. Test dengan curl manual
4. Review agent_utils.py implementation
5. Check LLM provider configuration