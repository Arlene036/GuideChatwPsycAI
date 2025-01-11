from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.monitor import DialogueMonitor
from app.core.security import SecurityManager

router = APIRouter()

class Message(BaseModel):
    role: str 
    content: str
    timestamp: Optional[datetime] = None

class DialogueInput(BaseModel):
    conversation_history: List[Message]
    session_id: str
    metadata: Optional[dict] = None  

class AnomalyDetail(BaseModel):
    type: str 
    severity: str  
    description: str
    recommendations: List[str]

class MonitoringResult(BaseModel):
    status: str  # "normal"  "alert"
    anomalies: List[AnomalyDetail] = []
    risk_level: str
    suggestions: List[str] = []
    security_status: Optional[dict] = None 

async def get_security_manager():
    return SecurityManager()

async def get_dialogue_monitor():
    return DialogueMonitor()

@router.post("/monitor", response_model=MonitoringResult)
async def monitor_dialogue(
    dialogue: DialogueInput,
    security_manager: SecurityManager = Depends(get_security_manager),
    dialogue_monitor: DialogueMonitor = Depends(get_dialogue_monitor)
):
    try:
        # 1. security check
        security_check = await security_manager.check_dialogue_safety(
            dialogue.conversation_history,
            dialogue.session_id
        )
        
        if security_check.get("severity") == "high":
            return MonitoringResult(
                status="alert",
                anomalies=[{
                    "type": "security",
                    "severity": "high",
                    "description": security_check.get("description", "检测到严重的安全问题"),
                    "recommendations": security_check.get("recommendations", ["请立即人工介入处理"])
                }],
                risk_level="high",
                security_status=security_check
            )
        
        # 2. monitor
        monitor_result = await dialogue_monitor.analyze(dialogue.conversation_history)
        
        # 3. 合并security和monitor结果
        if security_check.get("has_issues"):
            monitor_result["anomalies"].append({
                "type": "security",
                "severity": security_check["severity"],
                "description": security_check["description"],
                "recommendations": security_check["recommendations"]
            })
            
            if security_check["severity"] == "medium" and monitor_result["risk_level"] != "high":
                monitor_result["risk_level"] = "medium"
                
        monitor_result["security_status"] = security_check
        
        return MonitoringResult(**monitor_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "监控过程中出现错误",
                "session_id": dialogue.session_id
            }
        )

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
