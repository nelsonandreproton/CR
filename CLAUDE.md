# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based todo application with Telegram bot integration. The app serves a single-page web interface for managing todos and sends notifications to a configured Telegram bot when new todos are created.

## Architecture

- **Single-file application**: All logic is contained in `main.py`
- **In-memory storage**: Todos are stored in a global list (no database)
- **Hybrid rendering**: Server-side HTML generation with client-side JavaScript for interactions
- **Async notification system**: Telegram notifications are sent asynchronously without blocking user responses

### Key Components

- **Todo class**: Simple data model with id, text, and completed status
- **HTML generation**: `generate_html()` function creates the entire page with inline CSS/JS
- **API endpoints**:
  - `GET /` - Serves the main HTML page
  - `POST /add` - Creates new todo and triggers Telegram notification
  - `POST /toggle/{todo_id}` - Toggles todo completion status
  - `POST /delete/{todo_id}` - Deletes a todo
- **Telegram integration**: `send_telegram_notification()` sends formatted messages using httpx

## Development Commands

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the application
```bash
source venv/bin/activate
python main.py
```
Server runs on http://localhost:8000

### Installing new dependencies
```bash
source venv/bin/activate
pip install <package>
pip freeze > requirements.txt
```

## Configuration

Environment variables are loaded from `.env`:
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `TELEGRAM_CHAT_ID` - Target chat ID for notifications

Missing Telegram configuration will log warnings but won't break the app.

## Key Implementation Details

- **Security**: User input is HTML-escaped to prevent XSS
- **Error handling**: Proper HTTP status codes with detailed error messages
- **Async patterns**: Telegram notifications use `asyncio.create_task()` to avoid blocking
- **Input validation**: Todo text limited to 500 chars, Telegram messages truncated at 4096 chars
- **Client-side**: Full page reloads after operations (no SPA framework)
- **Logging**: Uses Python's logging module at INFO level

## Telegram Notification Format
New todos trigger formatted HTML messages with emoji, escaped text, and partial todo ID.