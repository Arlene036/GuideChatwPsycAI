from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PscyAgent"
    API_VERSION: str = "v1"
    
    # 异常检测阈值配置
    EMOTION_THRESHOLD: float = 0.7  # 情绪异常阈值
    RISK_THRESHOLD: float = 0.8     # 风险行为阈值
    
    # 响应时间配置
    MAX_RESPONSE_TIME: float = 2.0  # 秒
    
    class Config:
        env_file = ".env"

settings = Settings()