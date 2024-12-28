from datetime import datetime, timedelta
from typing import Dict
import hashlib
import re
class SecurityManager:
    def __init__(self):
        self.sensitive_patterns = [
            r"(密码|账号|身份证|银行卡)",
            r"(私密|机密|绝密)",
        ]
        
    def check_security(self, content: str) -> Dict:
        """检查内容是否包含敏感信息"""
        issues = []
        
        for pattern in self.sensitive_patterns:
            if re.search(pattern, content):
                issues.append({
                    "type": "security",
                    "severity": "high",
                    "description": "检测到潜在的敏感信息",
                    "recommendations": ["避免分享个人敏感信息"]
                })
                
        return issues