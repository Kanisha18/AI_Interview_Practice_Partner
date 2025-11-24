from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
from datetime import datetime

from app.models.session import InterviewSession
from app.services.conversation_manager import ConversationManager


router = APIRouter()

# In-memory session storage (replace with database in production)
sessions: Dict[str, InterviewSession] = {}


# ✅ Request models
class SessionCreate(BaseModel):
    role: str


class MessageRequest(BaseModel):
    session_id: str
    message: str


# ✅ Routes
@router.post("/api/interview/start")
async def start_interview(session_data: SessionCreate):
    """Start a new interview session"""
    
    print(f"\n🚀 Starting new interview for role: {session_data.role}")
    
    session = InterviewSession(
        id=str(datetime.utcnow().timestamp()),
        role=session_data.role,
        created_at=datetime.utcnow(),
        status="active"
    )
    
    sessions[session.id] = session
    conversation_manager = ConversationManager(session)
    
    result = await conversation_manager.start_interview()
    
    print(f"✅ Interview started with session_id: {session.id}")
    
    return {
        "session_id": session.id,
        **result
    }


@router.post("/api/interview/message")
async def process_message(message_req: MessageRequest):
    """Process user message and get next question or conclusion"""
    
    session = sessions.get(message_req.session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    conversation_manager = ConversationManager(session)
    result = await conversation_manager.process_user_response(message_req.message)
    
    # ✅ DEBUG: Log what we're sending to frontend
    print("\n" + "="*70)
    print("📡 API SENDING TO FRONTEND:")
    print("="*70)
    print(f"Type: {result.get('type')}")
    print(f"Interview complete: {result.get('interview_complete')}")
    print(f"Has feedback: {('feedback' in result)}")
    
    if 'feedback' in result:
        feedback = result['feedback']
        print(f"Feedback keys: {list(feedback.keys())}")
        print(f"Overall impression: {feedback.get('overall_impression', '')[:60]}...")
        print(f"Strengths: {len(feedback.get('strengths', []))} items")
        print(f"Improvements: {len(feedback.get('areas_for_improvement', []))} items")
        print(f"Next steps: {len(feedback.get('next_steps', []))} items")
    
    print("="*70 + "\n")
    
    return result


@router.get("/api/interview/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    
    session = sessions.get(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "role": session.role,
        "status": session.status,
        "created_at": session.created_at.isoformat(),
        "current_question": session.current_question_index,
        "persona": session.persona
    }


@router.delete("/api/interview/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted"}
    
    raise HTTPException(status_code=404, detail="Session not found")
