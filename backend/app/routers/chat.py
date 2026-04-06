from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Chat, ChatMessage
from ..schemas import (
    ChatCreate,
    ChatResponse,
    ChatListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
)
from ..utils.security import get_current_user_id
from ..services.ai_service import get_ai_response

router = APIRouter(prefix="/api/chats", tags=["Chats"])

SYSTEM_PROMPT = """You are an AI CV/Resume generator assistant. Your job is to help users create professional, ATS-optimized resumes.

Follow this conversation flow:
1. First, ask the user how many pages their CV should be (1 or 2 pages recommended).
2. Then ask for their information step by step:
   - Full name and contact info (email, phone, location)
   - Professional summary / objective
   - Work experience (company, role, duration, key achievements)
   - Education (degree, institution, year)
   - Technical and soft skills
   - Certifications (if any)
   - Notable projects (if any)
3. As the user provides information, ask clarifying follow-up questions.
4. When you have enough information, confirm with the user and tell them to click "Generate CV" to create their PDF.

Be conversational, professional, and helpful. Guide the user step by step. Keep your responses concise."""


@router.get("/", response_model=List[ChatListResponse])
def list_chats(
    user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)
):
    return (
        db.query(Chat)
        .filter(Chat.user_id == user_id)
        .order_by(Chat.created_at.desc())
        .all()
    )


@router.post("/", response_model=ChatResponse)
def create_chat(
    chat_data: ChatCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    chat = Chat(user_id=user_id, title=chat_data.title or "New Chat")
    db.add(chat)
    db.commit()
    db.refresh(chat)

    # Initial assistant greeting
    initial_msg = ChatMessage(
        chat_id=chat.id,
        role="assistant",
        content=(
            "Hello! I'm your AI CV Generator. I'll help you create a "
            "professional, ATS-optimized resume.\n\n"
            "First, **how many pages** should your CV be?\n"
            "(I recommend 1 page for early career, 2 pages for experienced professionals)"
        ),
    )
    db.add(initial_msg)
    db.commit()
    db.refresh(chat)

    return chat


@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
    chat_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.delete("/{chat_id}")
def delete_chat(
    chat_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted"}


@router.post("/{chat_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    chat_id: int,
    msg: ChatMessageCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Save user message
    user_msg = ChatMessage(chat_id=chat_id, role="user", content=msg.content)
    db.add(user_msg)
    db.commit()

    # Update chat title from first user message
    user_msg_count = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id, ChatMessage.role == "user")
        .count()
    )
    if user_msg_count == 1:
        chat.title = msg.content[:50] + ("..." if len(msg.content) > 50 else "")
        db.commit()

    # Build conversation history
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        conversation.append({"role": m.role, "content": m.content})

    # Get AI response
    ai_text = await get_ai_response(conversation)

    ai_msg = ChatMessage(chat_id=chat_id, role="assistant", content=ai_text)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return ai_msg
