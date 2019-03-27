""""""
import logging

from piz_base import AbstractException, AbstractClassPlugin
from piz_component.redis.redis_i import IRedisAdapter

logger = logging.getLogger(__name__)


class RedisClient(AbstractClassPlugin):
    def __init__(self):
        super(RedisClient, self).__init__()
        self.adapter = None

    def initialize(self, config: dict):
        from piz_component.redis.plugin import DefaultAdapter

        self._update_config(config)
        ins = self.load_plugin("classpath", DefaultAdapter())
        self.adapter = self.cast(ins, IRedisAdapter)
        logger.info("redis initialized,config={}".format(config))

    def get_processor(self):
        return self.adapter.get_processor()

    def _log(self, msg, e=None):
        if e and isinstance(e, AbstractException):
            logger.error(e.get_message())
        else:
            logger.debug(msg)

    def destroy(self, timeout=0):
        self.unload_plugin(self.adapter, timeout)
        logger.info("redis destroyed,timeout={}".format(timeout))
