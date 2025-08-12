# Telegram Bot Webhook API

A FastAPI-based Telegram bot webhook that handles messages, processes intents, and provides automated responses.

## Features

- **Message Processing**: Extracts chat_id, username, and message text or photo_id
- **User Management**: Automatically creates users in database if they don't exist
- **Intent Classification**: Detects if messages are questions, orders, or receipts
- **AI Integration**: Uses GPT for answering questions
- **Order Processing**: Handles order-related messages
- **Receipt Handling**: Processes receipt photos
- **Fallback Logging**: Logs unprocessed messages for review

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your configuration:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
```

3. Run the server:
```bash
python telegram_webhook.py
```

## API Endpoints

- `POST /telegram/webhook` - Main webhook endpoint for Telegram messages
- `GET /health` - Health check endpoint

## Database Schema

- **User**: Stores Telegram user information
- **Message**: Logs all incoming messages with intent classification

## Intent Classification

- **question**: Messages asking for information (uses GPT)
- **order**: Order-related messages (processed by order handler)
- **receipt**: Photo messages (processed by receipt handler)
- **fallback**: Unrecognized messages (logged for review)