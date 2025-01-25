from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time
from app.core.monitor import DialogueMonitor
from app.core.security import SecurityManager
import asyncio
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
    start_time = time.time()
    try:
        # 记录各个阶段的时间
        security_start = time.time()
        security_check, monitor_result = await asyncio.gather(
            security_manager.check_dialogue_safety(
                dialogue.conversation_history,
                dialogue.session_id
            ),
            dialogue_monitor.analyze(dialogue.conversation_history)
        )
        security_end = time.time()
        
        processing_start = time.time()
        if security_check.get("severity") == "high":
            result = MonitoringResult(
                status="alert",
                anomalies=[{
                    "type": "security",
                    "severity": "high",
                    "description": security_check.get("description", "检测到严重的安全问题"),
                }],
                risk_level="high",
                security_status=security_check
            )
        else:
            if security_check.get("has_issues"):
                monitor_result["anomalies"].append({
                    "type": "security",
                    "severity": security_check["severity"],
                    "description": security_check["description"],
                })
                
                if security_check["severity"] == "medium" and monitor_result["risk_level"] != "high":
                    monitor_result["risk_level"] = "medium"
                    
            monitor_result["security_status"] = security_check
            result = MonitoringResult(**monitor_result)
        
        # 计算各阶段耗时
        end_time = time.time()
        performance_metrics = {
            "total_latency": round(end_time - start_time, 2),
            "security_check_latency": round(security_end - security_start, 2),
            "processing_latency": round(end_time - processing_start, 2),
            "timestamp": datetime.now().isoformat()
        }

        print(f"性能指标: {performance_metrics}")
        
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
