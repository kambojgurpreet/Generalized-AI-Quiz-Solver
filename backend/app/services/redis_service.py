import redis.asyncio as redis
import json
import hashlib
import os
from typing import Optional, Any
from dotenv import load_dotenv

load_dotenv()

class RedisService:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.ttl = int(os.getenv("CACHE_TTL", 3600))  # 1 hour default
        self._client = None

    async def get_client(self) -> redis.Redis:
        """Get Redis client instance"""
        if self._client is None:
            try:
                # Try to connect using URL first
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            except Exception:
                # Fallback to host/port connection
                self._client = redis.Redis(
                    host=self.redis_host,
                    port=self.redis_port,
                    db=self.redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
        return self._client

    async def ping(self) -> bool:
        """Test Redis connection"""
        try:
            client = await self.get_client()
            await client.ping()
            return True
        except Exception as e:
            print(f"Redis ping failed: {e}")
            return False

    def _generate_cache_key(self, prefix: str, data: str) -> str:
        """Generate a cache key from data"""
        hash_object = hashlib.md5(data.encode())
        return f"{prefix}:{hash_object.hexdigest()}"

    async def cache_mcq_extraction(self, content: str, mcqs: list) -> Optional[str]:
        """Cache extracted MCQs"""
        try:
            client = await self.get_client()
            cache_key = self._generate_cache_key("mcq_extraction", content)
            
            from datetime import datetime
            cache_data = {
                "mcqs": mcqs,
                "extracted_at": datetime.now().isoformat()
            }
            
            await client.setex(
                cache_key,
                self.ttl,
                json.dumps(cache_data, default=str)
            )
            return cache_key
        except Exception as e:
            print(f"Redis unavailable, skipping cache write: {e}")
            return None

    async def get_cached_mcq_extraction(self, content: str) -> Optional[list]:
        """Get cached MCQ extraction"""
        try:
            client = await self.get_client()
            cache_key = self._generate_cache_key("mcq_extraction", content)
            
            cached_data = await client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return data.get("mcqs")
            return None
        except Exception as e:
            print(f"Redis unavailable, skipping cache lookup: {e}")
            return None

    async def cache_mcq_answer(self, question: str, options: list, answer_data: dict) -> Optional[str]:
        """Cache MCQ answer"""
        try:
            client = await self.get_client()
            question_key = f"{question}:{':'.join(options)}"
            cache_key = self._generate_cache_key("mcq_answer", question_key)
            
            from datetime import datetime
            cache_data = {
                "answer_data": answer_data,
                "answered_at": datetime.now().isoformat()
            }
            
            await client.setex(
                cache_key,
                self.ttl,
                json.dumps(cache_data, default=str)
            )
            return cache_key
        except Exception as e:
            print(f"Error caching MCQ answer: {e}")
            return None

    async def get_cached_mcq_answer(self, question: str, options: list) -> Optional[dict]:
        """Get cached MCQ answer"""
        try:
            client = await self.get_client()
            question_key = f"{question}:{':'.join(options)}"
            cache_key = self._generate_cache_key("mcq_answer", question_key)
            
            cached_data = await client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return data.get("answer_data")
            return None
        except Exception as e:
            print(f"Error getting cached MCQ answer: {e}")
            return None

    async def cache_full_page_analysis(self, url: str, content: str, analysis_result: dict) -> Optional[str]:
        """Cache full page analysis result"""
        try:
            client = await self.get_client()
            page_key = f"{url}:{len(content)}"  # Include content length as simple hash
            cache_key = self._generate_cache_key("page_analysis", page_key)
            
            from datetime import datetime
            cache_data = {
                "url": url,
                "analysis_result": analysis_result,
                "analyzed_at": datetime.now().isoformat()
            }
            
            await client.setex(
                cache_key,
                self.ttl * 2,  # Cache page analysis longer
                json.dumps(cache_data, default=str)
            )
            return cache_key
        except Exception as e:
            print(f"Error caching page analysis: {e}")
            return None

    async def get_cached_page_analysis(self, url: str, content: str) -> Optional[dict]:
        """Get cached page analysis"""
        try:
            client = await self.get_client()
            page_key = f"{url}:{len(content)}"
            cache_key = self._generate_cache_key("page_analysis", page_key)
            
            cached_data = await client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return data.get("analysis_result")
            return None
        except Exception as e:
            print(f"Error getting cached page analysis: {e}")
            return None

    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()

# Use datetime instead of pandas for timestamp
from datetime import datetime