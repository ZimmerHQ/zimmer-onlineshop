# LangChain Tool-Calling Agent

This document explains the new LangChain-based tool-calling agent that replaces the previous ad-hoc logic.

## Overview

The agent uses LangChain's tool-calling patterns with a clean separation between:
- **System prompt** (short, focused instructions)
- **Tool definitions** (clear schemas and descriptions)
- **Agent logic** (thin routing layer)

## Architecture

### 1. System Prompt (`SYSTEM`)
- Short, focused instructions in English
- Persian (Farsi) output language
- Clear behavior rules for different scenarios

### 2. Tools (`@tool` decorators)
- `featured_products()` - Show popular items for greeting/fallback
- `get_by_code()` - Fetch exact product by code
- `search_semantic()` - RAG/semantic search
- `search_fuzzy()` - Database fuzzy search
- `make_order()` - Create order after confirmation

### 3. Agent Logic
- **With LLM**: Uses LangChain's `create_tool_calling_agent`
- **Without LLM**: Falls back to simple rule-based logic
- **Selection handling**: Processes "1", "2", "3" selections

## Usage

### With OpenAI API Key
```python
# Set environment variable
export OPENAI_API_KEY="your-api-key"

# Agent will use full LLM capabilities
result = sales_agent_turn(db, "سلام", {})
```

### Without API Key (Fallback Mode)
```python
# Agent automatically falls back to rule-based logic
result = sales_agent_turn(db, "سلام", {})
```

## Key Features

### 1. Tool-Calling Pattern
- Model decides when to call tools based on descriptions
- Clean separation of concerns
- Easy to add new tools

### 2. Fallback Mechanism
- Works without OpenAI API key
- Graceful degradation to rule-based logic
- Maintains core functionality

### 3. Persian Language Support
- Natural Persian responses
- Proper number formatting (٬ for thousands)
- Cultural context awareness

### 4. Sales-Focused Behavior
- "همچین محصولی نداریم، اما این گزینه‌ها نزدیک هستن…" (never "چیزی پیدا نکردم")
- Product selection by number
- Order confirmation flow

## Tool Descriptions

Each tool has a clear, directive description that guides the LLM:

```python
@tool
def featured_products(limit: int = 3) -> str:
    """Return up to N popular items for greeting/fallback. Use when user greets or you need safe suggestions."""
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY` - Required for full LLM functionality
- `OPENAI_MODEL` - Model to use (default: "gpt-4o-mini")

### Database Session
The agent requires a database session to be set:
```python
from backend.ai.agent import set_db_session
set_db_session(db_session)
```

## Testing

The agent can be tested with various scenarios:

1. **Greeting**: "سلام" → Featured products + examples
2. **Product Code**: "A0001" → Exact product details
3. **Search**: "شلوار" → RAG → fuzzy → featured
4. **Selection**: "1" → Select from last list
5. **Description**: "توضیحات" → Official DB description

## Benefits

### 1. LangChain Best Practices
- Tool-calling over long prompts
- Clear tool schemas
- Model-driven tool selection

### 2. Maintainability
- Easy to add new tools
- Clear separation of concerns
- Testable components

### 3. Flexibility
- Works with or without LLM
- Easy to customize behavior
- Extensible architecture

### 4. Performance
- Efficient tool calling
- Minimal prompt overhead
- Fast fallback mode

## Migration from Previous Agent

The new agent maintains backward compatibility:
- Same function signature: `sales_agent_turn(db, message, state)`
- Same return format: `{"reply": str, "state": dict}`
- Same state management patterns

## Future Enhancements

1. **LangGraph Integration**: For complex multi-step workflows
2. **More Tools**: Add tools for specific business logic
3. **Streaming**: Real-time response streaming
4. **Memory**: Persistent conversation memory
5. **Analytics**: Tool usage tracking and optimization
