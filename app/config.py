from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PscyAgent"
    API_VERSION: str = "v1"

    # if choose to use openai, set OPENAI_API_KEY
    OPENAI_API_KEY: str = "your_openai_api_key"
    MODEL_NAME: str = "gpt-4o-mini" # default model
    # if deploy on local
    BASE_URL: str = ""# "http://localhost:8001/v1"
    DUMMPY_API_KEY: str = "dummy_api_key"
    TEMPERATURE: float = 0.1

    ############################################################
    EMOTION_THRESHOLD: float = 0.7  
    RISK_THRESHOLD: float = 0.8    
    
    MAX_RESPONSE_TIME: float = 2.0  # seconds
    
    class Config:
        env_file = ".env"

settings = Settings()