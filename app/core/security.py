from datetime import datetime, timedelta
from typing import Dict, List
import logging
from pathlib import Path
from fastapi import BackgroundTasks
from openai import AsyncOpenAI
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def check_dialogue_safety(
        self, 
        conversation_history: List[Dict],
        session_id: str
    ) -> Dict:
        """检查对话的安全性和合规性"""
        
        messages = [
            {"role": "system", "content": """
            你是一个对话安全审核专家。请分析对话内容的安全性和合规性，重点关注：
            1. 敏感个人信息（如身份证、银行卡、密码等）
            2. 违法违规内容（如暴力、犯罪、极端言论等）
            3. 不当内容（如色情、歧视、骚扰等）
            4. 数据安全风险（如信息泄露、隐私侵犯等）
            5. 政治敏感内容
            
            请以JSON格式返回分析结果：
            {
                "has_issues": bool,
                "severity": "low|medium|high",
                "risk_types": [检测到的风险类型],
                "description": "详细描述",
                "recommendations": [建议措施],
                "requires_immediate_action": bool
            }
            """}
        ]
        
        for msg in conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            }) 
            
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=messages,
                response_format={ "type": "json_object" },
                temperature=0.1
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            
            analysis["session_id"] = session_id
            analysis["timestamp"] = datetime.now().isoformat()
            
            if analysis["requires_immediate_action"]:
                analysis["recommendations"].extend([
                    "立即中断当前对话",
                    "记录相关信息",
                    "通知相关负责人"
                ])
            
            await self._log_security_event(analysis) if analysis["has_issues"] else None
            
            return analysis
            
        except Exception as e:
            return {
                "has_issues": True,
                "severity": "medium",
                "risk_types": ["system_error"],
                "description": f"安全检查过程中出现错误: {str(e)}",
                "recommendations": [
                    "建议人工审核对话内容",
                    "暂时采取保守的安全策略"
                ],
                "requires_immediate_action": False,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            