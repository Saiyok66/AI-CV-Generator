# Architecture

## System Overview

```
┌─────────────────┐     HTTP/REST      ┌──────────────────┐
│                  │ ◄────────────────► │                  │
│  React Frontend  │     /api/*         │  FastAPI Backend  │
│  (Vite + TW)     │                    │                  │
│  Port: 5173      │                    │  Port: 8000      │
└─────────────────┘                    └────────┬─────────┘
                                                │
                                    ┌───────────┼───────────┐
                                    │           │           │
                                    ▼           ▼           ▼
                               ┌────────┐ ┌────────┐ ┌──────────┐
                               │ SQLite │ │ Ollama │ │ReportLab │
                               │   DB   │ │  LLM   │ │  PDF Gen │
                               └────────┘ └────────┘ └──────────┘
```

## Data Flow

1. User interacts with React frontend
2. Frontend sends API requests to FastAPI backend (proxied via Vite)
3. Backend authenticates via JWT
4. Chat messages are sent to Ollama for AI responses
5. CV data is extracted and structured by AI
6. ReportLab generates professional PDF
7. PDF is stored locally and served for download

## Database Schema

- **users**: id, username, email, hashed_password, created_at
- **chats**: id, user_id, title, created_at
- **chat_messages**: id, chat_id, role, content, created_at
- **resumes**: id, user_id, chat_id, filename, filepath, page_count, created_at
