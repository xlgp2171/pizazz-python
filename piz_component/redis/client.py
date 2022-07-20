""" redis实例

"""
import logging

from piz_base import AbstractClassPlugin, ICloseable
from piz_base.base_e import BaseRuntimeException
from piz_component.redis.redis_i import IRedisAdapter, IRedisProcessor

logger = logging.getLogger(__name__)


class RedisLoader(AbstractClassPlugin):
    def __init__(self, configure):
        from piz_component.redis.plugin import SingleAdapter

        super(RedisLoader, self).__init__(configure)
        ins = self.load_plugin("classpath", SingleAdapter())
        self.adapter: IRedisAdapter = self.cast(ins, IRedisAdapter)
        self.adapter.initialize(self.get_config())
        logger.info("redis initialized,config={}".format(configure))

    def _log(self, msg, e=None):
        if e and isinstance(e, BaseRuntimeException):
            logger.error(e.get_message())
        else:
            logger.debug(msg)

    def destroy(self, timeout=0):
        self.unload_plugin(self.adapter, timeout)
        logger.info("redis destroyed,timeout={}".format(timeout))


class RedisClient(ICloseable):
    def __init__(self, configure):
        self._loader = RedisLoader(configure)

    def get_processor(self) -> IRedisProcessor:
        return self._loader.adapter.get_processor()

    def destroy(self, timeout=0):
        self._loader.destroy(timeout)
