from datetime import datetime, timedelta
from typing import Dict, List
import logging
from pathlib import Path
import time
from fastapi import BackgroundTasks
from openai import AsyncOpenAI
from app.config import settings
from app.core.model_client import OpenAIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self):
        self.client = OpenAIClient()
        
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
        
        cont = ""
        for msg in conversation_history:
            cont += f"{msg.role}: {msg.content}\n"
        messages.append({"role": 'user', "content": cont})
            
        try:
            start_time = time.time()
            response_content = await self.client.generate(
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            end_time = time.time()
            
            start_processing = time.time()
            import json
            import re
            if "```" in response_content:
                pattern = r"```(?:json)?\n?(.*?)```"
                match = re.search(pattern, response_content, re.DOTALL)
                if match:
                    response_content = match.group(1).strip()
            
            analysis = json.loads(response_content)
            end_processing = time.time()

            analysis["session_id"] = session_id
            analysis["timestamp"] = datetime.now().isoformat()
            
            if analysis["requires_immediate_action"]:
                analysis["recommendations"].extend([
                    "立即中断当前对话",
                    "记录相关信息",
                    "通知相关负责人"
                ])
            
            end_time = time.time()
            time_metrics = {
                "total_latency": round(end_time - start_time, 2),
                "response_latency": round(end_time - start_time, 2),
                "processing_latency": round(end_processing - start_processing, 2),
            }
            print(f"\n\nSecurity性能指标: {time_metrics}\n\n")
            
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
            