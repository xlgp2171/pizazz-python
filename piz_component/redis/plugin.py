""""""
from redis import Redis, ConnectionPool

from piz_component.redis.redis_i import IRedisProcessor, IRedisAdapter


class DefaultAdapter(IRedisAdapter):
    def __init__(self):
        self.pool = None

    def initialize(self, config):
        if isinstance(config, dict):
            pool_config = config.get("client", {})
            pool = ConnectionPool(**pool_config)
            self.pool = Redis(
                connection_pool=pool)

    def get_processor(self):
        return DefaultProcessor(self.pool)

    def destroy(self, timeout=0):
        if self.pool:
            self.pool.connection_pool.disconnect()


class DefaultProcessor(IRedisProcessor):
    def __init__(self, pool):
        if isinstance(pool, Redis):
            self.pool = pool

    def set(self, key, value):
        return self.bset(key, value)

    def bset(self, key, value):
        return self.pool.set(key, value)

    def hmset(self, key, set_map):
        return self.pool.hmset(key, set_map)

    def hset(self, key, field, value):
        return self.pool.hset(key, field, value)

    def get(self, key, encoding="UTF-8"):
        return str(
            self.bget(key),
            encoding=encoding)

    def bget(self, key):
        return self.pool.get(key)

    def hget(self, key, field):
        return self.pool.hget(key, field)

    def hmget(self, key):
        return self.pool.hgetall(key)

    def hdel(self, key, field):
        return self.pool.hdel(key, field)

    def delete(self, *key):
        return self.pool.delete(*key)

    def keys(self, pattern):
        return self.pool.keys(pattern)
