from openai import AsyncOpenAI
from typing import List, Dict
from app.config import settings
import asyncio


class OpenAIClient():
    def __init__(self):
        if settings.BASE_URL=="" and settings.DEEPSEEK_API_KEY == "":
            print("====Using OpenAI API====")
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        elif settings.DEEPSEEK_API_KEY != "":
            self.client = AsyncOpenAI(
                base_url="https://api.deepseek.com/v1",
                api_key=settings.DEEPSEEK_API_KEY
            )
            print("====Using DeepSeek API====")
        else:
            print("====Using Dummy API====")
            self.client = AsyncOpenAI(
                base_url=settings.BASE_URL, 
                api_key=settings.DUMMPY_API_KEY
            )
    
    async def generate(self, messages: List[Dict], **kwargs) -> str:
        print("====Generating response====")
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

if __name__ == "__main__":
    async def main():
        client = OpenAIClient()
        messages = [{"role": "user", "content": "Hello, how are you?"}]
        response = await client.generate(messages)
        print(response)
    
    asyncio.run(main())