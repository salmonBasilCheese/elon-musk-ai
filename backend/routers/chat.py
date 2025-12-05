"""
Chat API Router
Handles conversation endpoints for the Elon AI dialogue system
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import asyncio
import logging

from services.thinking_engine import ThinkingEngine
from services.openai_client import OpenAIClient
from services.usage_tracker import usage_tracker
from rate_limiter import limiter



# Initialize services
thinking_engine = ThinkingEngine()
openai_client = OpenAIClient()
usage_tracker = usage_tracker


    """Single chat message"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request payload"""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message (max 2000 chars)")
    conversation_history: Optional[List[ChatMessage]] = Field(default=[], description="Previous messages")
    mode: Optional[str] = Field(default="standard", description="Thinking mode: 'standard', 'first_principles', 'strategy'")


class ChatResponse(BaseModel):
    """Chat response payload"""
    message: str = Field(..., description="AI response")
    thinking_process: Optional[str] = Field(None, description="Simplified thinking process (optional)")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    mode_used: str = Field(..., description="Thinking mode applied")


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: ChatRequest, req: Request):
    """
    Main chat endpoint
    Processes user message through Musk-style thinking engine
    Rate limited to stay within free tier
    """
    start_time = datetime.now()
    
    # Check rate limit FIRST
    allowed, reason = usage_tracker.can_make_request()
    if not allowed:
        logger.warning(f"Rate limit exceeded: {reason}")
        raise HTTPException(status_code=429, detail=reason)
    
    try:
        logger.info(f"Received chat request: {request.message[:50]}...")
        
        # Apply thinking engine to enhance the prompt
        enhanced_prompt = thinking_engine.apply_thinking_style(
            user_message=request.message,
            mode=request.mode,
            history=request.conversation_history
        )
        
        # Get response from OpenAI with timeout
        try:
            response = await asyncio.wait_for(
                openai_client.get_response(enhanced_prompt),
                timeout=60.0  # 60 second max
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504,
                detail="Response timeout. Processing took longer than 60 seconds."
            )
        
        # Record usage for rate limiting
        total_tokens = response.get("usage", {}).get("prompt_tokens", 0) + response.get("usage", {}).get("completion_tokens", 0)
        usage_tracker.record_request(total_tokens)
        
        # Calculate response time
        end_time = datetime.now()
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        logger.info(f"Response generated in {response_time_ms}ms, tokens used: {total_tokens}")
        
        return ChatResponse(
            message=response["content"],
            thinking_process=response.get("thinking_summary"),
            response_time_ms=response_time_ms,
            mode_used=request.mode
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/chat/stream")
@limiter.limit("20/minute")
async def chat_stream(request: ChatRequest, req: Request):
    """
    Streaming chat endpoint for real-time responses
    Rate limited to stay within free tier
    """
    # Check rate limit FIRST
    allowed, reason = usage_tracker.can_make_request()
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)
    
    try:
        enhanced_prompt = thinking_engine.apply_thinking_style(
            user_message=request.message,
            mode=request.mode,
            history=request.conversation_history
        )
        
        async def generate():
            async for chunk in openai_client.get_response_stream(enhanced_prompt):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
            # Record usage (approximate for streaming)
            usage_tracker.record_request(500)
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modes")
async def get_thinking_modes():
    """
    Get available thinking modes
    """
    return {
        "modes": [
            {
                "id": "standard",
                "name": "標準思考",
                "description": "バランスの取れた分析と提案"
            },
            {
                "id": "first_principles",
                "name": "第一原理思考",
                "description": "問題を根本から分解し、ゼロベースで再構築"
            },
            {
                "id": "strategy",
                "name": "戦略シミュレーション",
                "description": "高インパクト・高リスク戦略の探索"
            }
        ]
    }


@router.get("/usage")
async def get_usage_stats():
    """
    Get current API usage statistics
    Helps monitor free tier usage
    """
    return usage_tracker.get_usage_stats()
