from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PscyAgent"
    API_VERSION: str = "v1"

    # if choose to use openai, set OPENAI_API_KEY
    OPENAI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    # if deploy on local
    BASE_URL: str = ""# "http://localhost:8000/v1"
    DUMMPY_API_KEY: str = "dummy_api_key"
    TEMPERATURE: float = 0.1 # default temperature

    MODEL_NAME: str = "deepseek-chat" # default model, choose from [chatglm2-6B, deepseek-chat, ...]

    ############################################################
    
    class Config:
        env_file = ".env"

settings = Settings()
