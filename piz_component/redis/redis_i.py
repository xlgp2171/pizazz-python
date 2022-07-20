""" Redis实例接口

"""
from piz_base import IPlugin


class IRedisAdapter(IPlugin):
    def get_processor(self):
        raise NotImplementedError("not supported 'get_processor'")


class IRedisProcessor(object):
    def set(self, key: str, value: str):
        raise NotImplementedError("not supported 'set'")

    def get_string(self, key: str, encoding="UTF-8"):
        raise NotImplementedError("not supported 'get_string'")

    def set_binary(self, key: str, value):
        raise NotImplementedError("not supported 'set_binary'")

    def get_binary(self, key: str):
        raise NotImplementedError("not supported 'get_binary'")

    def set_all_map(self, key: str, set_map: dict):
        raise NotImplementedError("not supported 'set_all_map'")

    def get_all_map(self, key: str):
        raise NotImplementedError("not supported 'get_all_map'")

    def get_map_by_key(self, key: str, *fields: str):
        raise NotImplementedError("not supported 'get_map_by_key'")

    def remove(self, *key: str):
        raise NotImplementedError("not supported 'remove'")

    def keys(self, pattern: str, encoding='UTF-8'):
        raise NotImplementedError("not supported 'keys'")
