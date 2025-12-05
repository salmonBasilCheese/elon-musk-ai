"""
Rate Limiting and Usage Control Service
Prevents excessive API calls and monitors token usage
"""
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class UsageTracker:
    """
    Tracks API usage to prevent exceeding free tier limits
    
    OpenAI Free Tier Limits (approximate):
    - GPT-4o-mini: ~200 RPM, ~200K TPM
    - Daily budget recommendation: Stay under $5/day
    """
    
    # Conservative limits to stay well within free tier
    MAX_REQUESTS_PER_MINUTE = 10
    MAX_REQUESTS_PER_HOUR = 50
    MAX_REQUESTS_PER_DAY = 200
    MAX_TOKENS_PER_REQUEST = 1000  # Limit response length
    MAX_TOKENS_PER_DAY = 50000
    
    def __init__(self):
        self.requests: list = []
        self.daily_tokens: int = 0
        self.last_reset: datetime = datetime.now()
        self._cleanup_interval = timedelta(hours=1)
    
    def _cleanup_old_requests(self):
        """Remove requests older than 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        self.requests = [r for r in self.requests if r["timestamp"] > cutoff]
        
        # Reset daily token counter at midnight
        if datetime.now().date() > self.last_reset.date():
            self.daily_tokens = 0
            self.last_reset = datetime.now()
            logger.info("Daily token counter reset")
    
    def can_make_request(self) -> tuple[bool, Optional[str]]:
        """
        Check if a new request is allowed
        Returns: (allowed, reason if blocked)
        """
        self._cleanup_old_requests()
        now = datetime.now()
        
        # Check per-minute limit
        minute_ago = now - timedelta(minutes=1)
        recent_minute = sum(1 for r in self.requests if r["timestamp"] > minute_ago)
        if recent_minute >= self.MAX_REQUESTS_PER_MINUTE:
            wait_time = 60 - (now - self.requests[-1]["timestamp"]).seconds
            return False, f"レート制限: 1分あたり{self.MAX_REQUESTS_PER_MINUTE}回まで。{wait_time}秒後に再試行してください。"
        
        # Check per-hour limit
        hour_ago = now - timedelta(hours=1)
        recent_hour = sum(1 for r in self.requests if r["timestamp"] > hour_ago)
        if recent_hour >= self.MAX_REQUESTS_PER_HOUR:
            return False, f"レート制限: 1時間あたり{self.MAX_REQUESTS_PER_HOUR}回まで。しばらくお待ちください。"
        
        # Check daily limit
        day_ago = now - timedelta(hours=24)
        recent_day = sum(1 for r in self.requests if r["timestamp"] > day_ago)
        if recent_day >= self.MAX_REQUESTS_PER_DAY:
            return False, f"1日の上限（{self.MAX_REQUESTS_PER_DAY}回）に達しました。明日再試行してください。"
        
        # Check daily token limit
        if self.daily_tokens >= self.MAX_TOKENS_PER_DAY:
            return False, f"1日のトークン上限（{self.MAX_TOKENS_PER_DAY}）に達しました。"
        
        return True, None
    
    def record_request(self, tokens_used: int = 0):
        """Record a successful request"""
        self.requests.append({
            "timestamp": datetime.now(),
            "tokens": tokens_used
        })
        self.daily_tokens += tokens_used
        logger.info(f"Request recorded. Daily tokens: {self.daily_tokens}/{self.MAX_TOKENS_PER_DAY}")
    
    def get_usage_stats(self) -> dict:
        """Get current usage statistics"""
        self._cleanup_old_requests()
        now = datetime.now()
        
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(hours=24)
        
        return {
            "requests_last_minute": sum(1 for r in self.requests if r["timestamp"] > minute_ago),
            "requests_last_hour": sum(1 for r in self.requests if r["timestamp"] > hour_ago),
            "requests_last_24h": sum(1 for r in self.requests if r["timestamp"] > day_ago),
            "tokens_today": self.daily_tokens,
            "limits": {
                "per_minute": self.MAX_REQUESTS_PER_MINUTE,
                "per_hour": self.MAX_REQUESTS_PER_HOUR,
                "per_day": self.MAX_REQUESTS_PER_DAY,
                "tokens_per_day": self.MAX_TOKENS_PER_DAY
            }
        }


# Global singleton instance
usage_tracker = UsageTracker()
