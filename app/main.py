from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings
import uvicorn

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="AI对话监控系统 - 检测并预防对话中的异常情况"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")