""""""
from piz_base import IPlugin


class IRedisAdapter(IPlugin):
    def get_processor(self):
        raise NotImplementedError("not supported 'get_processor'")


class IRedisProcessor(object):
    def set(self, key, value):
        raise NotImplementedError("not supported 'set'")

    def bset(self, key, value):
        raise NotImplementedError("not supported 'bset'")

    def hmset(self, key, set_map):
        raise NotImplementedError("not supported 'hmset'")

    def hset(self, key, field, value):
        raise NotImplementedError("not supported 'hset'")

    def get(self, key, encoding="UTF-8"):
        raise NotImplementedError("not supported 'get'")

    def bget(self, key):
        raise NotImplementedError("not supported 'bget'")

    def hget(self, key, field):
        raise NotImplementedError("not supported 'hget'")

    def hmget(self, key):
        raise NotImplementedError("not supported 'hmget'")

    def hdel(self, key, field):
        raise NotImplementedError("not supported 'hdel'")

    def delete(self, *key):
        raise NotImplementedError("not supported 'dele'")

    def keys(self, pattern):
        raise NotImplementedError("not supported 'keys'")
