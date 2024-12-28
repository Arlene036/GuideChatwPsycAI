from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class Message(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: Optional[datetime] = None

class DialogueInput(BaseModel):
    conversation_history: List[Message]
    session_id: str

class AnomalyDetail(BaseModel):
    type: str  # "emotional", "behavioral", "technical", "security"
    severity: str  # "low", "medium", "high"
    description: str
    recommendations: List[str]

class MonitoringResult(BaseModel):
    status: str  # "normal" 或 "alert"
    anomalies: List[AnomalyDetail] = []
    risk_level: str
    suggestions: List[str] = []

@router.post("/monitor", response_model=MonitoringResult)
async def monitor_dialogue(dialogue: DialogueInput):
    try:
        from app.core.monitor import DialogueMonitor
        monitor = DialogueMonitor()
        result = await monitor.analyze(dialogue.conversation_history)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))