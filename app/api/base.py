from utils.caching import DataCache

class Base:
    def __init__(self, cache_ttl: int):
        self.cache = DataCache(ttl=cache_ttl)

    def _cache_key(self, *args, **kwargs) -> str:
        """Generate a cache key based on the input parameters"""
        key_parts= [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return "_".join(key_parts)
    
    def name(self):
        return self.__class__.__name__