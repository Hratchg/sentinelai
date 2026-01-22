"""
Chat API endpoint for conversational surveillance queries.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging

from backend.storage.database import get_db
from backend.llm.query_engine import SurveillanceQueryEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class VideoClip(BaseModel):
    """Video clip reference in chat response."""
    clip_url: str
    person_id: str
    timestamp: str
    event_type: str


class ChatRequest(BaseModel):
    """Chat request from user."""
    message: str
    include_clips: bool = True


class ChatResponse(BaseModel):
    """Chat response with optional video clips."""
    answer: str
    video_clips: List[VideoClip] = []
    sources: List[Dict] = []


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db = Depends(get_db)
):
    """
    Conversational interface with surveillance AI.

    Ask natural language questions about surveillance data:
    - "Who is that person on camera 1?"
    - "When did I last see John?"
    - "What is Sarah doing right now?"
    - "Show me all times Michael visited this week"

    The AI will:
    1. Retrieve relevant context from database
    2. Use Claude LLM to answer question
    3. Attach video clips as evidence (if available)

    Args:
        request: Chat request with user question
        db: Database session

    Returns:
        ChatResponse with answer and optional video clips
    """
    try:
        # Initialize query engine
        engine = SurveillanceQueryEngine()

        # Get answer from LLM
        result = await engine.answer_question(
            db_session=db,
            question=request.message,
            include_clips=request.include_clips
        )

        # Convert video clips to Pydantic models
        video_clips = [
            VideoClip(**clip)
            for clip in result.get('video_clips', [])
        ]

        return ChatResponse(
            answer=result['answer'],
            video_clips=video_clips,
            sources=result.get('sources', [])
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return ChatResponse(
            answer=f"Sorry, I encountered an error: {str(e)}",
            video_clips=[],
            sources=[]
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for chat service."""
    return {
        "status": "healthy",
        "service": "chat"
    }
