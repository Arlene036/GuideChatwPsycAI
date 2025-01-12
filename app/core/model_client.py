from openai import AsyncOpenAI
from typing import List, Dict
from app.config import settings

class OpenAIClient():
    def __init__(self):
        if settings.BASE_URL=="":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = AsyncOpenAI(
                base_url=settings.BASE_URL, 
                api_key=settings.DUMMPY_API_KEY 
            )
    
    async def generate(self, messages: List[Dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=kwargs.get("temperature", settings.TEMPERATURE)
        )
        return response.choices[0].message.content

class LocalModelClient():
    def __init__(self, model_path: str):
        self.model = self._load_model(model_path)
    
    async def generate(self, messages: List[Dict], **kwargs) -> str:
        pass