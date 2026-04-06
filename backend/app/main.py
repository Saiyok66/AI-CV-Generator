from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, chat, resume

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI CV Generator",
    description="AI-powered CV/Resume generator using local LLM",
    version="1.0.0",
)

from .config import FRONTEND_URL

allowed_origins = [
    "http://localhost:5173",
    FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(resume.router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "AI CV Generator API is running"}
