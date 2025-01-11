from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PscyAgent"
    API_VERSION: str = "v1"
    OPENAI_API_KEY: str = "your_openai_api_key"
    
    EMOTION_THRESHOLD: float = 0.7  
    RISK_THRESHOLD: float = 0.8    
    
    MAX_RESPONSE_TIME: float = 2.0  # second
    
    class Config:
        env_file = ".env"

settings = Settings()