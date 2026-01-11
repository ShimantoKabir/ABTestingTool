import json
import redis # type: ignore
from typing import Optional, Any
from config import Config

class CacheService:
  def __init__(self):
    self.client = redis.from_url(Config.getValByKey("REDIS_URL"))
    self.defaultTtl = 1 # 60 seconds

  def get(self, key: str) -> Optional[Any]:
    data = self.client.get(key)
    if data:
      return json.loads(data)
    return None

  def set(self, key: str, value: Any, ttl: int = None):
    expiry = ttl if ttl is not None else self.defaultTtl
    jsonData = json.dumps(value, default=str) 
    self.client.setex(key, expiry, jsonData)

  def delete(self, key: str):
    self.client.delete(key)