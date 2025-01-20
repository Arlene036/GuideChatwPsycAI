from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PscyAgent"
    API_VERSION: str = "v1"

    # if choose to use openai, set OPENAI_API_KEY
    OPENAI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    # if deploy on local
    BASE_URL: str = ""# "http://localhost:8001/v1"
    DUMMPY_API_KEY: str = "dummy_api_key"
    TEMPERATURE: float = 0.1 # default temperature

    MODEL_NAME: str = "gpt-4o-mini" # default model, choose like [chatglm2-6B]

    ############################################################

    
    class Config:
        env_file = ".env"

settings = Settings()
