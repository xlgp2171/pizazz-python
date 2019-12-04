""""""
from redis import Redis, ConnectionPool
from rediscluster import RedisCluster

from piz_component.redis.redis_i import IRedisProcessor, IRedisAdapter


class ClusterAdapter(IRedisAdapter):
    def __init__(self):
        self.__instance: RedisCluster = None

    def initialize(self, config):
        if isinstance(config, dict):
            cluster_config = config.get("client", {})
            self.__instance = RedisCluster(**cluster_config)

    def get_processor(self):
        return DefaultProcessor(self.__instance)

    def destroy(self, timeout=0):
        if self.__instance:
            self.__instance.connection_pool.disconnect()


class DefaultAdapter(IRedisAdapter):
    def __init__(self):
        self.__pool = None

    def initialize(self, config):
        if isinstance(config, dict):
            pool_config = config.get("client", {})
            pool = ConnectionPool(**pool_config)
            self.__pool = Redis(
                connection_pool=pool)

    def get_processor(self):
        return DefaultProcessor(self.__pool)

    def destroy(self, timeout=0):
        if self.__pool:
            self.__pool.connection_pool.disconnect()


class DefaultProcessor(IRedisProcessor):
    def __init__(self, instance):
        if isinstance(instance, Redis) or isinstance(instance, RedisCluster):
            self.instance = instance

    def set(self, key, value):
        return self.bset(key, value)

    def bset(self, key, value):
        return self.instance.set(key, value)

    def hmset(self, key, set_map):
        return self.instance.hmset(key, set_map)

    def hset(self, key, field, value):
        return self.instance.hset(key, field, value)

    def get(self, key, encoding="UTF-8"):
        return str(
            self.bget(key),
            encoding=encoding)

    def bget(self, key):
        return self.instance.get(key)

    def hget(self, key, field):
        return self.instance.hget(key, field)

    def hmget(self, key):
        return self.instance.hgetall(key)

    def hdel(self, key, field):
        return self.instance.hdel(key, field)

    def delete(self, *key):
        return self.instance.delete(*key)

    def keys(self, pattern):
        return self.instance.keys(pattern)
