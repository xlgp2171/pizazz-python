""" Redis操作实现

"""
from redis import Redis, ConnectionPool, RedisCluster

from piz_component.redis.redis_i import IRedisProcessor, IRedisAdapter


class ClusterAdapter(IRedisAdapter):
    def __init__(self):
        self._instance = None

    def initialize(self, config):
        if isinstance(config, dict):
            cluster_config = config.get("client", {})
            self._instance = RedisCluster(**cluster_config)

    def get_processor(self):
        return DefaultProcessor(self._instance)

    def destroy(self, timeout=0):
        if self._instance:
            self._instance.connection_pool.disconnect()


class SingleAdapter(IRedisAdapter):
    def __init__(self):
        self._pool = None

    def initialize(self, config):
        if isinstance(config, dict):
            pool_config = config.get("client", {})
            pool = ConnectionPool(**pool_config)
            self._pool = Redis(
                connection_pool=pool)

    def get_processor(self):
        return DefaultProcessor(self._pool)

    def destroy(self, timeout=0):
        if self._pool:
            self._pool.connection_pool.disconnect()


class DefaultProcessor(IRedisProcessor):
    def __init__(self, instance):
        if isinstance(instance, Redis) or isinstance(instance, RedisCluster):
            self._instance = instance

    def set(self, key: str, value: str):
        return self.set_binary(key, value)

    # noinspection PyTypeChecker
    def get_string(self, key: str, encoding="UTF-8"):
        tmp = self.get_binary(key)
        return str(tmp, encoding=encoding) if tmp else ""

    def set_binary(self, key: str, value):
        return self._instance.set(key, value)

    def get_binary(self, key: str):
        return self._instance.get(key)

    def set_all_map(self, key: str, set_map: dict):
        return self._instance.hset(key, mapping=set_map)

    def get_all_map(self, key: str):
        return self._instance.hgetall(key)

    def get_map_by_key(self, key: str, *fields: str):
        return self._instance.hmget(key, *fields)

    def remove(self, *key: str):
        return self._instance.delete(*key)

    def keys(self, pattern: str, encoding='UTF-8'):
        keys = self._instance.keys(pattern)
        return [str(x, encoding=encoding) for x in keys]
