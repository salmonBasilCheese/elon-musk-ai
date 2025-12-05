"""
OpenAI API Client Service
Handles communication with OpenAI API for response generation
With cost controls for free tier usage
"""
from openai import AsyncOpenAI
from typing import AsyncGenerator
import logging

from config import settings
from services.usage_tracker import UsageTracker

logger = logging.getLogger(__name__)

# Cost-controlled token limits
MAX_TOKENS_PER_RESPONSE = 800  # Reduced from 2000 to save costs


class OpenAIClient:
    """
    Async OpenAI API client for generating responses
    Configured for minimal cost while maintaining quality
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        logger.info(f"OpenAI client initialized with model: {self.model}")
        logger.info(f"Max tokens per response: {MAX_TOKENS_PER_RESPONSE}")
    
    async def get_response(self, prompt_data: dict) -> dict:
        """
        Get a complete response from OpenAI
        
        Args:
            prompt_data: Dictionary containing 'messages' and 'mode'
            
        Returns:
            Dictionary with 'content' and optional 'thinking_summary'
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=prompt_data["messages"],
                temperature=0.7,  # Slightly reduced for more focused responses
                max_tokens=MAX_TOKENS_PER_RESPONSE,  # Cost-controlled limit
                presence_penalty=0.4,
                frequency_penalty=0.2
            )
            
            content = response.choices[0].message.content
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = prompt_tokens + completion_tokens
            
            logger.info(f"Response: {len(content)} chars, {total_tokens} tokens (in:{prompt_tokens}, out:{completion_tokens})")
            
            return {
                "content": content,
                "thinking_summary": self._get_mode_summary(prompt_data.get("mode", "standard")),
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def get_response_stream(self, prompt_data: dict) -> AsyncGenerator[str, None]:
        """
        Get a streaming response from OpenAI
        
        Args:
            prompt_data: Dictionary containing 'messages' and 'mode'
            
        Yields:
            Response chunks as strings
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=prompt_data["messages"],
                temperature=0.7,
                max_tokens=MAX_TOKENS_PER_RESPONSE,
                presence_penalty=0.4,
                frequency_penalty=0.2,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {str(e)}")
            raise
    
    def _get_mode_summary(self, mode: str) -> str:
        """Get thinking process summary based on mode"""
        summaries = {
            "standard": "戦略的分析フレームワークを適用",
            "first_principles": "第一原理思考で問題を分解・再構築",
            "strategy": "高インパクト戦略シミュレーションを実行"
        }
        return summaries.get(mode, "分析完了")
