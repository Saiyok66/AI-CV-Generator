# 🤖 AI CV Generator

A full-stack, AI-powered CV/Resume generator that runs **entirely locally** using open-source tools. Built with React, FastAPI, and Ollama for local LLM inference.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?logo=tailwindcss)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black)

---

## ✨ Features

- **AI-Powered CV Generation** — Uses local LLM (Ollama + LLaMA3/Mistral) for intelligent resume creation
- **ATS Optimized** — Generates resumes optimized for Applicant Tracking Systems
- **Real-time Processing Steps** — Live visualization of CV generation stages
- **Professional PDF Output** — Clean, formatted PDFs using ReportLab
- **Chat Interface** — Intuitive conversational UI for data collection
- **User Authentication** — Secure JWT-based login/signup
- **Chat History** — Persistent conversation history per user
- **100% Local & Free** — No paid APIs, everything runs on your machine

---

## 🛠️ Tech Stack

| Layer       | Technology                        |
| ----------- | --------------------------------- |
| Frontend    | React 18, Vite 5, Tailwind CSS 3 |
| Backend     | Python FastAPI, SQLAlchemy        |
| Database    | SQLite                            |
| AI Model    | Ollama (LLaMA3 / Mistral)        |
| PDF Engine  | ReportLab                         |
| Auth        | JWT (python-jose + passlib)       |

---

## 🏗️ Architecture

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

---

## 📁 Project Structure

```
AI-CV-Generator/
├── frontend/                  # React + Vite frontend
│   ├── src/
│   │   ├── api/               # API client utilities
│   │   ├── components/        # Reusable UI components
│   │   ├── context/           # React context (auth state)
│   │   ├── pages/             # Page components
│   │   ├── App.jsx            # Root component with routing
│   │   ├── main.jsx           # Entry point
│   │   └── index.css          # Tailwind imports & global styles
│   ├── package.json
│   ├── vite.config.js         # Vite config with API proxy
│   └── tailwind.config.js
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── routers/           # API route handlers
│   │   │   ├── auth.py        # Login / Signup endpoints
│   │   │   ├── chat.py        # Chat CRUD + AI messaging
│   │   │   └── resume.py      # CV generation + download
│   │   ├── services/          # Business logic
│   │   │   ├── ai_service.py  # Ollama LLM integration
│   │   │   └── pdf_service.py # ReportLab PDF generation
│   │   ├── utils/
│   │   │   └── security.py    # JWT + password hashing
│   │   ├── config.py          # App configuration
│   │   ├── database.py        # SQLAlchemy DB setup
│   │   ├── models.py          # ORM models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   └── main.py            # FastAPI application
│   ├── requirements.txt
│   └── run.py                 # Dev server launcher
├── database/                  # SQLite DB & generated PDFs
├── docs/                      # Documentation
├── .gitignore
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites

- **Node.js** 18+ — [nodejs.org](https://nodejs.org)
- **Python** 3.10+ — [python.org](https://python.org)
- **Ollama** — [ollama.ai](https://ollama.ai)

### 1. Clone the Repository

```bash
git clone https://github.com/Saiyok66/AI-CV-Generator.git
cd AI-CV-Generator
```

### 2. Install & Start Ollama

```bash
# Download Ollama from https://ollama.ai and install it
# Then pull a model:
ollama pull llama3

# Ollama runs automatically in the background after installation
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
python run.py
```

The API server starts at `http://localhost:8000`

### 4. Frontend Setup (new terminal)

```bash
cd frontend
npm install
npm run dev
```

The app opens at `http://localhost:5173`

---

## 🎯 How to Use

1. **Sign Up** — Create an account on the signup page
2. **Start a Chat** — Click "New Chat" to begin
3. **Follow AI Prompts** — The AI will ask for your CV details step by step
4. **Select Page Count** — Choose 1 or 2 pages from the header dropdown
5. **Generate CV** — Click "Generate CV" to create your resume
6. **Download PDF** — Click the download button to save your CV

---

## 📸 Screenshots

> *Add screenshots after running the application*

| Login Page | Dashboard | Generated CV |
|:---:|:---:|:---:|
| ![Login](docs/screenshots/login.png) | ![Dashboard](docs/screenshots/dashboard.png) | ![CV](docs/screenshots/cv.png) |

---

## 🧪 Sample Test Input

```
Page count: 1

Name: John Smith
Email: john.smith@email.com
Phone: +1 (555) 123-4567
Location: San Francisco, CA

Summary: Full-stack developer with 5 years of experience building
scalable web applications using React, Python, and cloud technologies.

Experience:
- Senior Software Engineer at TechCorp (2022 - Present)
  - Led migration of monolithic app to microservices, reducing deployment time by 60%
  - Built real-time analytics dashboard serving 10K+ daily users

- Software Engineer at StartupXYZ (2020 - 2022)
  - Developed RESTful APIs using FastAPI, handling 1M+ requests/day
  - Implemented CI/CD pipeline reducing release cycles from weeks to days

Education:
- B.S. Computer Science, Stanford University (2020)

Skills: Python, JavaScript, React, FastAPI, Docker, AWS, PostgreSQL, Git
```

---

## 🔮 Future Enhancements

- [ ] Multiple CV templates (Modern, Classic, Creative)
- [ ] LinkedIn profile import
- [ ] Cover letter generation
- [ ] Resume scoring & ATS analysis
- [ ] Export to DOCX format
- [ ] Dark/Light theme toggle
- [ ] Multi-language support
- [ ] Resume version history & comparison

---

## 📄 License

MIT License — feel free to use this project for learning and portfolio purposes.

---

Built with ❤️ using React, FastAPI, and Ollama
