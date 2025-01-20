from typing import List, Dict
from openai import AsyncOpenAI
from app.config import settings
from app.core.model_client import OpenAIClient
import asyncio

class DialogueMonitor:
    def __init__(self):
        self.client = OpenAIClient()
        
    async def analyze(self, conversation: List[Dict]) -> Dict:
        result = {
            "status": "normal",
            "anomalies": [],
            "risk_level": "low",
            "suggestions": []
        }
        
        emotional_issues, behavioral_issues, quality_issues = await asyncio.gather(
            self._check_emotional_state(conversation),
            self._check_behavioral_patterns(conversation),
            self._check_ai_response_quality(conversation)
        )
        
        all_issues = emotional_issues + behavioral_issues + quality_issues
        
        if all_issues:
            result["status"] = "alert"
            result["anomalies"] = all_issues
            result["risk_level"] = self._determine_risk_level(all_issues)
            result["suggestions"] = await self._generate_suggestions(all_issues)
            
        return result
    
    async def _check_emotional_state(self, conversation: List[Dict]) -> List[Dict]:
        issues = []
        
        messages = [
            {"role": "system", "content": """
            你是一个专业的心理健康分析助手。请分析用户的对话内容，识别：
            1. 情绪状态（特别是负面情绪）
            2. 自我伤害风险
            3. 心理危机信号
            
            请以JSON格式返回分析结果，包含以下字段：
            {
                "emotional_state": {
                    "has_negative": bool,
                    "severity": "low|medium|high",
                    "emotions": [具体情绪],
                    "description": "描述"
                },
                "risk_assessment": {
                    "has_risk": bool,
                    "severity": "low|medium|high",
                    "risk_types": [风险类型],
                    "description": "描述"
                },
                "recommendations": [建议列表]
            }
            """}
        ]
        
        for msg in conversation:
            if msg.role == "user":
                messages.append({"role": "user", "content": msg.content})
        
        try:
            response_content = await self.client.generate(
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            analysis = json.loads(response_content)
            
            if analysis["emotional_state"]["has_negative"]:
                issues.append({
                    "type": "emotional",
                    "severity": analysis["emotional_state"]["severity"],
                    "description": analysis["emotional_state"]["description"],
                    "recommendations": analysis["recommendations"]
                })
            
            if analysis["risk_assessment"]["has_risk"]:
                issues.append({
                    "type": "risk",
                    "severity": analysis["risk_assessment"]["severity"],
                    "description": analysis["risk_assessment"]["description"],
                    "recommendations": analysis["recommendations"]
                })
                
        except Exception as e:
            issues.append({
                "type": "system",
                "severity": "low",
                "description": f"情绪分析_check_emotional_state过程中出现错误: {str(e)}",
                "recommendations": ["请人工复查对话内容"]
            })
            
        return issues
    
    async def _check_behavioral_patterns(self, conversation: List[Dict]) -> List[Dict]:
        issues = []
        
        messages = [
            {"role": "system", "content": """
            你是一个对话行为分析专家。请分析用户的对话行为模式，识别：
            1. 重复性行为（重复提问、重复要求）
            2. 攻击性或不当言论
            3. 不合理请求
            4. 对AI的不信任表现
            
            请以JSON格式返回分析结果：
            {
                "behavioral_issues": {
                    "has_issues": bool,
                    "severity": "low|medium|high",
                    "patterns": [检测到的行为模式],
                    "description": "描述"
                },
                "interaction_quality": {
                    "is_problematic": bool,
                    "severity": "low|medium|high",
                    "issues": [交互问题],
                    "description": "描述"
                },
                "recommendations": [建议列表]
            }
            """}
        ]
        
        recent_messages = conversation[-10:]  # TODO
        for msg in recent_messages:
            messages.append({"role": msg.role, "content": msg.content})
            
        try:
            response_content = await self.client.generate(
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            analysis = json.loads(response_content)
            if analysis["behavioral_issues"]["has_issues"]:
                issues.append({
                    "type": "behavioral",
                    "severity": analysis["behavioral_issues"]["severity"],
                    "description": analysis["behavioral_issues"]["description"],
                    "recommendations": analysis["recommendations"]
                })
                
            if analysis["interaction_quality"]["is_problematic"]:
                issues.append({
                    "type": "interaction",
                    "severity": analysis["interaction_quality"]["severity"],
                    "description": analysis["interaction_quality"]["description"],
                    "recommendations": analysis["recommendations"]
                })
                
        except Exception as e:
            issues.append({
                "type": "system",
                "severity": "low",
                "description": f"行为分析过程中出现错误: {str(e)}",
                "recommendations": ["请人工检查对话行为模式"]
            })
            
        return issues
        
    async def _check_ai_response_quality(self, conversation: List[Dict]) -> List[Dict]:
        issues = []
        
        messages = [
            {"role": "system", "content": """
            你是一个AI响应质量审核专家。请分析AI的回复质量，识别：
            1. 回答是否符合用户期待
            2. 信息准确性和完整性
            3. 语言表达的适当性
            4. 回答的连贯性和逻辑性
            5. 是否存在敏感或不当内容
            
            请以JSON格式返回分析结果：
            {
                "response_quality": {
                    "has_issues": bool,
                    "severity": "low|medium|high",
                    "issues": [质量问题],
                    "description": "描述"
                },
                "content_safety": {
                    "has_issues": bool,
                    "severity": "low|medium|high",
                    "issues": [安全问题],
                    "description": "描述"
                },
                "recommendations": [建议列表]
            }
            """}
        ]
        
        for i, msg in enumerate(conversation):
            if msg.role == "assistant":
                if i > 0:
                    messages.append({"role": conversation[i-1].role, 
                                   "content": conversation[i-1].content})
                messages.append({"role": msg.role, "content": msg.content})
        
        try:
            response_content = await self.client.generate(
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            analysis = json.loads(response_content)
            
            if analysis["response_quality"]["has_issues"]:
                issues.append({
                    "type": "quality",
                    "severity": analysis["response_quality"]["severity"],
                    "description": analysis["response_quality"]["description"],
                    "recommendations": analysis["recommendations"]
                })
                
            if analysis["content_safety"]["has_issues"]:
                issues.append({
                    "type": "safety",
                    "severity": analysis["content_safety"]["severity"],
                    "description": analysis["content_safety"]["description"],
                    "recommendations": analysis["recommendations"]
                })
                
        except Exception as e:
            issues.append({
                "type": "system",
                "severity": "low",
                "description": f"AI响应质量分析过程中出现错误: {str(e)}",
                "recommendations": ["请人工检查AI响应质量"]
            })
            
        return issues
        
    def _determine_risk_level(self, issues: List[Dict]) -> str:
        """根据所有发现的问题确定整体风险等级"""
        severity_scores = {
            "low": 1,
            "medium": 2,
            "high": 3
        }
        
        max_severity = 0
        for issue in issues:
            severity = severity_scores.get(issue["severity"], 0)
            max_severity = max(max_severity, severity)
            
        if max_severity >= 3:
            return "high"
        elif max_severity == 2:
            return "medium"
        else:
            return "low"
            
    async def _generate_suggestions(self, issues: List[Dict]) -> List[str]:
        """生成综合建议"""
        if not issues:
            return []
            
        messages = [
            {"role": "system", "content": """
            基于以下问题列表，生成一个综合的建议列表。建议应该：
            1. 具体且可执行
            2. 按优先级排序
            3. 避免重复
            4. 措辞积极正面
            仅返回建议列表，每条建议一行。
            """},
            {"role": "user", "content": str(issues)}
        ]
        
        try:
            response_content = await self.client.generate(
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            suggestions = response_content.strip().split("\n")
            return [s.strip("- ") for s in suggestions if s.strip()]
            
        except Exception:
            return list(set([rec for issue in issues 
                           for rec in issue.get("recommendations", [])]))
    
    