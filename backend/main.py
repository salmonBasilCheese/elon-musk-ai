"""
Elon-Inspired Strategic Dialogue AI - Backend API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routers import chat
from config import settings
from rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("🚀 Starting Elon AI Backend...")
    logger.info(f"OpenAI API Key configured: {'Yes' if settings.openai_api_key else 'No'}")
    yield
    logger.info("👋 Shutting down Elon AI Backend...")


app = FastAPI(
    title="Elon-Inspired Strategic Dialogue AI",
    description="マスク的思考スタイルで回答するAI対話エンジン",
    version="1.0.0",
    lifespan=lifespan
)

# Rate Limiter Setup (Enabled)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
# Restrict to trusted domains in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://elon-musk-ai.vercel.app", 
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "elon-ai-backend",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Elon-Inspired Strategic Dialogue AI API",
        "docs": "/docs",
        "health": "/health"
    }
