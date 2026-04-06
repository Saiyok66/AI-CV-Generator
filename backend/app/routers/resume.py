from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio
from ..database import get_db
from ..models import Chat, ChatMessage, Resume
from ..schemas import ResumeResponse, GenerateRequest
from ..utils.security import get_current_user_id
from ..services.ai_service import extract_cv_data
from ..services.pdf_service import generate_cv_pdf

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


@router.get("/", response_model=List[ResumeResponse])
def list_resumes(
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    return (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )


@router.post("/generate")
async def generate_resume(
    req: GenerateRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == req.chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == req.chat_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    conversation_text = "\n".join([f"{m.role}: {m.content}" for m in messages])

    async def event_stream():
        steps = [
            "Understanding input",
            "Structuring data",
            "Optimizing for ATS",
            "Formatting CV",
            "Generating PDF",
        ]

        # Step 1: Understanding input — also triggers AI extraction
        yield f"data: {json.dumps({'step': steps[0], 'index': 0})}\n\n"
        cv_data = await extract_cv_data(conversation_text)

        # Step 2: Structuring data
        yield f"data: {json.dumps({'step': steps[1], 'index': 1})}\n\n"
        await asyncio.sleep(0.5)

        # Step 3: Optimizing for ATS
        yield f"data: {json.dumps({'step': steps[2], 'index': 2})}\n\n"
        await asyncio.sleep(0.5)

        # Step 4: Formatting CV
        yield f"data: {json.dumps({'step': steps[3], 'index': 3})}\n\n"
        await asyncio.sleep(0.5)

        # Step 5: Generating PDF
        yield f"data: {json.dumps({'step': steps[4], 'index': 4})}\n\n"
        filepath, filename = generate_cv_pdf(cv_data, req.page_count, user_id)

        # Persist resume record
        resume = Resume(
            user_id=user_id,
            chat_id=req.chat_id,
            filename=filename,
            filepath=filepath,
            page_count=req.page_count,
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)

        yield f"data: {json.dumps({'step': 'complete', 'resume_id': resume.id, 'filename': filename})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/{resume_id}/download")
def download_resume(
    resume_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user_id).first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return FileResponse(
        path=resume.filepath,
        filename=resume.filename,
        media_type="application/pdf",
    )
