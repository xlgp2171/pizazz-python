""""""
from piz_base import IPlugin


class IRedisAdapter(IPlugin):
    def get_processor(self):
        raise NotImplementedError("not supported 'get_processor'")


class IRedisProcessor(object):
    def set(self, key: str, value: str):
        raise NotImplementedError("not supported 'set'")

    def bset(self, key: str, value):
        raise NotImplementedError("not supported 'bset'")

    def hmset(self, key: str, set_map: dict):
        raise NotImplementedError("not supported 'hmset'")

    def hset(self, key: str, field: str, value):
        raise NotImplementedError("not supported 'hset'")

    def get(self, key: str, encoding="UTF-8"):
        raise NotImplementedError("not supported 'get'")

    def bget(self, key: str):
        raise NotImplementedError("not supported 'bget'")

    def hget(self, key: str, field: str):
        raise NotImplementedError("not supported 'hget'")

    def hmget(self, key: str):
        raise NotImplementedError("not supported 'hmget'")

    def hdel(self, key: str, field: str):
        raise NotImplementedError("not supported 'hdel'")

    def delete(self, *key: str):
        raise NotImplementedError("not supported 'dele'")

    def keys(self, pattern: str):
        raise NotImplementedError("not supported 'keys'")
