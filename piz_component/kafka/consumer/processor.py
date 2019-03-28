""""""
import logging

from piz_base import AbstractClassPlugin, AbstractException
from piz_component.kafka.consumer.consumer_i import IProcessAdapter, IBridge

logger = logging.getLogger(__name__)


class DataProcessor(AbstractClassPlugin):
    def __init__(self, offset, mode, ignore):
        super(DataProcessor, self).__init__()
        self.__offset = offset
        self.__mode = mode
        self.__ignore = ignore
        self.__adapter = None

    def initialize(self, config):
        from piz_component.kafka.consumer.plugin import SequenceAdapter

        self._set_config(config)
        ins = self.load_plugin("classpath", SequenceAdapter(), True)
        self.__adapter = self.cast(ins, IProcessAdapter)
        self.__adapter.set(self.__mode)
        logger.info("subscription data processor initialized,config={}".format(config))

    def optimize_kafka_config(self, kafka_config):
        return kafka_config if self.__mode else kafka_config

    def consume_ready(self, consumer, executor):
        if consumer and self.__mode:
            executor.begin()

    def consume(self, consumer, record, executor):
        offset = self.__offset

        class BridgeCls(IBridge):
            def get_id(self):
                return "{}#{}#{}#{}".format(record.topic, record.partition, record.offset, record.timestamp)

            def passing(self):
                executor.execute(record)
                offset.each(consumer, record)

        self.__adapter.accept(BridgeCls(), self.__ignore)

    def consume_complete(self, consumer, executor, e=None):
        if e:
            executor.throw_exception(e)
        else:
            executor.end(self.__offset)
        self.__offset.complete(consumer, e)

    def monitor(self):
        return self.__adapter.monitor()

    def _log(self, msg, e=None):
        if e and isinstance(e, AbstractException):
            logger.error(e.get_message())
        else:
            logger.debug(msg)

    def destroy(self, timeout=0):
        self.unload_plugin(self.__adapter, timeout)
        logger.info("subscription data processor destroyed,timeout={}".format(timeout))
