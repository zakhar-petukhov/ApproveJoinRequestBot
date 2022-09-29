from cachetools import TTLCache
from datetime import datetime, timedelta

cache_data = TTLCache(maxsize=50000, ttl=timedelta(minutes=7), timer=datetime.now)
