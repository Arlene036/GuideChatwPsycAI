from typing import List, Dict
import re
from app.config import settings

class DialogueMonitor:
    def __init__(self):
        self.emotional_patterns = {
            "negative": [
                r"(不想|厌倦|痛苦|绝望|自杀|死亡)",
                r"(焦虑|抑郁|悲伤|愤怒|恐惧)",
            ],
            "risk": [
                r"(自残|伤害|结束生命)",
                r"(放弃|无助|没有希望)",
            ]
        }
        
    async def analyze(self, conversation: List[Dict]) -> Dict:
        result = {
            "status": "normal",
            "anomalies": [],
            "risk_level": "low",
            "suggestions": []
        }
        
        # 分析最近的对话
        emotional_issues = self._check_emotional_state(conversation)
        behavioral_issues = self._check_behavioral_patterns(conversation)
        quality_issues = self._check_ai_response_quality(conversation)
        
        # 整合所有发现的问题
        all_issues = emotional_issues + behavioral_issues + quality_issues
        
        if all_issues:
            result["status"] = "alert"
            result["anomalies"] = all_issues
            result["risk_level"] = self._determine_risk_level(all_issues)
            result["suggestions"] = self._generate_suggestions(all_issues)
            
        return result
    
    def _check_emotional_state(self, conversation: List[Dict]) -> List[Dict]:
        issues = []
        for message in conversation:
            if message["role"] != "user":
                continue
                
            content = message["content"]
            # 检查负面情绪
            for pattern in self.emotional_patterns["negative"]:
                if re.search(pattern, content):
                    issues.append({
                        "type": "emotional",
                        "severity": "medium",
                        "description": "检测到强烈的负面情绪表达",
                        "recommendations": ["建议温和回应", "表达同理心"]
                    })
                    
            # 检查风险行为
            for pattern in self.emotional_patterns["risk"]:
                if re.search(pattern, content):
                    issues.append({
                        "type": "emotional",
                        "severity": "high",
                        "description": "检测到潜在的自我伤害风险",
                        "recommendations": ["立即介入专业帮助", "保持积极支持"]
                    })
        return issues