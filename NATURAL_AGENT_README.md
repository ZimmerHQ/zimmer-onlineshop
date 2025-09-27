# Natural Persian Sales Agent

This system replaces the rigid phrase matching with a natural Persian sales agent using LangChain/LangGraph.

## Features

- **RAG over products**: Semantic search over product names, codes, descriptions, labels, and attributes
- **Structured extraction**: Extracts quantity, size, color, product_code, and confirmation from natural Persian input
- **Natural conversation**: Human, non-scripted tone with Persian responses
- **Flexible confirmations**: Recognizes various confirmation phrases (تایید/باشه/بله/اوکی/etc.)
- **Fallback system**: Works without OpenAI API key using regex-based extraction

## Components

### 1. RAG System (`backend/ai/rag.py`)
- Builds FAISS vector index over all products
- Uses OpenAI embeddings for semantic search
- In-memory singleton with rebuild capability

### 2. Structured Extraction (`backend/ai/slots.py`)
- Pydantic model for extracting structured data from natural language
- Fields: product_code, quantity, size, color, confirm

### 3. Sales Agent (`backend/ai/agent.py`)
- Natural conversation flow with Persian responses
- Uses LLM for slot extraction (with regex fallback)
- Integrates with existing tools for product search and order creation

### 4. Enhanced Tools (`backend/ai/tools.py`)
- Added `tool_rag_search()` for semantic product search
- Maintains existing product and order tools

## Usage

### With OpenAI API Key
Set the `OPENAI_API_KEY` environment variable for full functionality:
- Semantic product search via RAG
- Advanced slot extraction via LLM
- Natural conversation flow

### Without OpenAI API Key
The system falls back to:
- Keyword-based product search
- Regex-based slot extraction
- Basic conversation flow

## API Endpoints

### Chat
```
POST /api/chat
{
  "conversation_id": "default",
  "message": "می‌خوام کفش مشکی سایز ۴۲"
}
```

### Rebuild RAG Index (Dev)
```
POST /api/health/rebuild-rag
```

## Example Conversations

**User**: "A0001"  
**Agent**: "این محصول رو پیدا کردم 👇 • شلوار جین مردانه (کد A0001) 💵 قیمت: 150000 📦 موجودی: 50 چندتا می‌خوای؟ اگر سایز/رنگ مد نظرت هست بگو."

**User**: "۲ تا مشکی M"  
**Agent**: "خلاصه سفارش: • شلوار جین مردانه (کد A0001) • تعداد: 2 • سایز: M • رنگ: مشکی اگر اوکیه فقط بگو «تایید» یا «باشه»."

**User**: "تایید"  
**Agent**: "سفارش ثبت شد ✅ کد سفارش: ORD-2024-001 وضعیت: pending"

## Configuration

The system automatically detects available capabilities:
- If `OPENAI_API_KEY` is set: Full LLM-powered experience
- If not set: Falls back to regex-based extraction

## Development

To rebuild the RAG index after adding/editing products:
```bash
curl -X POST http://localhost:8000/api/health/rebuild-rag
```

## Integration

The natural agent is now the default for `/api/chat` endpoint. The system maintains backward compatibility with existing chat logging and frontend integration.
