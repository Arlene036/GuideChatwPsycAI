from typing import List, Dict
from openai import AsyncOpenAI
import time
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

        start_time = time.time()
        emotional_issues, behavioral_issues, quality_issues = await asyncio.gather(
            self._check_emotional_state(conversation),
            self._check_behavioral_patterns(conversation),
            self._check_ai_response_quality(conversation)
        )

        emotional_end = time.time()
        all_issues = emotional_issues + behavioral_issues + quality_issues
        # 合并所有建议,但是有的emotional_issues可能是[]，这样写会报错
        # all_suggestions = emotional_issues["suggestions"] + behavioral_issues["suggestions"] + quality_issues["suggestions"]
        all_suggestions = []
        count = 0
        for issue in emotional_issues + behavioral_issues + quality_issues:
            for suggestion in issue["suggestions"]:
                all_suggestions.append(f"{count}. {suggestion}")
                count += 1

        start_all_issues = time.time()
        if all_issues:
            result["status"] = "alert"
            result["anomalies"] = all_issues
            result["risk_level"] = self._determine_risk_level(all_issues)
            result["suggestions"] = all_suggestions
        end_all_issues = time.time()
        
        time_metrics = {
            "total_latency": round(end_all_issues - start_time, 2),
            "emotional_latency": round(emotional_end - start_time, 2),
            "suggestions_latency": round(end_all_issues - start_all_issues, 2),
        }
        print(f"\n\nMonitor性能指标: {time_metrics}\n\n")

        return result
    
    async def _check_emotional_state(self, conversation: List[Dict]) -> List[Dict]:
        issues = []
        
        messages = [
            {"role": "system", "content": """
            你是一个专业的心理健康监督助手，监督用户和心理健康AI机器人的对话。请分析用户和AI的对话内容，识别：
            1. 情绪状态（特别是负面情绪）
            2. 自我伤害风险(risk，比如自杀、自残等)
            3. 心理危机信号
            
            请以JSON格式返回分析结果，包含以下字段：
            {
                "risk_assessment": {
                    "has_risk": bool,
                    "severity": "low|medium|high",
                    "risk_types": [风险类型],
                    "description": "描述",
                    "suggestions": [建议心理健康AI机器人跟用户聊天时应该注意的事项, 30字以内]
                },
            }

            用户和AI的对话内容如下：
            """}
        ]
        
        cont = ""
        for msg in conversation:
            cont += f"{msg.role}: {msg.content}\n"
        messages.append({"role": 'user', "content": cont})
        
        try:
            response_content = await self.client.generate(
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            # print("====> check_emotional_state API Response:", response_content)

            import json
            import re
            if "```" in response_content:
                pattern = r"```(?:json)?\n?(.*?)```"
                match = re.search(pattern, response_content, re.DOTALL)
                if match:
                    response_content = match.group(1).strip()
            
            analysis = json.loads(response_content)
            
            if analysis["risk_assessment"]["has_risk"]:
                issues.append({
                    "type": "risk",
                    "severity": analysis["risk_assessment"]["severity"],
                    "description": analysis["risk_assessment"]["description"],
                    "suggestions": analysis["risk_assessment"]["suggestions"]
                })
                
        except Exception as e:
            issues.append({
                "type": "system",
                "severity": "low",
                "description": f"情绪分析_check_emotional_state过程中出现错误: {str(e)}"
            })
            
        return issues
    
    async def _check_behavioral_patterns(self, conversation: List[Dict]) -> List[Dict]:
        issues = []
        
        messages = [
            {"role": "system", "content": """
            你是一个专业的心理健康对话行为监督助手，监督用户和心理健康AI机器人的对话。请分析用户和AI的对话内容，识别：
            1. 用户提问的重复性行为（重复提问、重复要求）
            2. 用户的攻击性或不当言论
            3. 用户的不合理请求
            4. 用户对AI的不信任表现
            
            请以JSON格式返回分析结果：
            {
                "behavioral_issues": {
                    "has_issues": bool,
                    "severity": "low|medium|high",
                    "patterns": [检测到的行为模式],
                    "description": "描述",
                    "suggestions": [建议心理健康AI机器人跟用户聊天时应该注意的事项, 30字以内]
                },
                "interaction_quality": {
                    "is_problematic": bool,
                    "severity": "low|medium|high",
                    "issues": [交互问题],
                    "description": "描述",
                    "suggestions": [建议心理健康AI机器人跟用户聊天时应该注意的事项, 30字以内]
                },
            }
            用户和AI的对话内容如下：
            """}
        ]
        
        recent_messages = conversation[-10:]  # TODO
        cont = ""
        for msg in recent_messages:
            cont += f"{msg.role}: {msg.content}\n"
        messages.append({"role": 'user', "content": cont})
            
        try:
            response_content = await self.client.generate(
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            # print("====> check_behavioral_patterns API Response:", response_content)
            
            import json
            import re
            if "```" in response_content:
                pattern = r"```(?:json)?\n?(.*?)```"
                match = re.search(pattern, response_content, re.DOTALL)
                if match:
                    response_content = match.group(1).strip()
            
            analysis = json.loads(response_content)
            if analysis["behavioral_issues"]["has_issues"]:
                issues.append({
                    "type": "behavioral",
                    "severity": analysis["behavioral_issues"]["severity"],
                    "description": analysis["behavioral_issues"]["description"],
                    "suggestions": analysis["behavioral_issues"]["suggestions"]
                })
                
            if analysis["interaction_quality"]["is_problematic"]:
                issues.append({
                    "type": "interaction",
                    "severity": analysis["interaction_quality"]["severity"],
                    "description": analysis["interaction_quality"]["description"],
                    "suggestions": analysis["interaction_quality"]["suggestions"]
                })
                
        except Exception as e:
            issues.append({
                "type": "system",
                "severity": "low",
                "description": f"行为分析过程中出现错误: {str(e)}"
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
                    "description": "描述",
                    "suggestions": [建议心理健康AI机器人跟用户聊天时应该注意的事项, 30字以内]
                },
                "content_safety": {
                    "has_issues": bool,
                    "severity": "low|medium|high",
                    "issues": [安全问题],
                    "description": "描述",
                    "suggestions": [建议心理健康AI机器人跟用户聊天时应该注意的事项, 30字以内]
                },
            }
            用户和AI的对话内容如下：
            """}
        ]
        
        cont = ""
        for msg in conversation:
            cont += f"{msg.role}: {msg.content}\n"
        messages.append({"role": 'user', "content": cont})
        
        try:
            response_content = await self.client.generate(
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            import re
            if "```" in response_content:
                pattern = r"```(?:json)?\n?(.*?)```"
                match = re.search(pattern, response_content, re.DOTALL)
                if match:
                    response_content = match.group(1).strip()
            
            analysis = json.loads(response_content)
            
            if analysis["response_quality"]["has_issues"]:
                issues.append({
                    "type": "quality",
                    "severity": analysis["response_quality"]["severity"],
                    "description": analysis["response_quality"]["description"],
                    "suggestions": analysis["response_quality"]["suggestions"]
                })
                
            if analysis["content_safety"]["has_issues"]:
                issues.append({
                    "type": "safety",
                    "severity": analysis["content_safety"]["severity"],
                    "description": analysis["content_safety"]["description"],
                    "suggestions": analysis["content_safety"]["suggestions"]
                })
                
        except Exception as e:
            issues.append({
                "type": "system",
                "severity": "low",
                "description": f"AI响应质量分析过程中出现错误: {str(e)}"
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
            你是一个监督用户与心理医生(AI机器人)聊天的监督助手，基于察觉到的聊天记录的问题列表，生成一个综合的建议列表，引导心理医生(AI机器人)如何与用户沟通。建议应该：
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
            # print("====> _generate_suggestions API Response:", response_content)
            suggestions = response_content.strip().split("\n")
            return [s.strip("- ") for s in suggestions if s.strip()]
            
        except Exception:
            return ['_generate_suggestions过程中出现错误']
    
    