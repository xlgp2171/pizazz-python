""" 订阅处理类

"""
import logging

from piz_base import AbstractClassPlugin, ICloseable
from piz_base.base_e import BaseRuntimeException
from piz_component.kafka.consumer.consumer_i import IProcessAdapter, IBridge

logger = logging.getLogger(__name__)


class DataProcessor(AbstractClassPlugin, ICloseable):
    def __init__(self, offset, mode, ignore, config):
        super(DataProcessor, self).__init__(config)
        self._offset = offset
        self._ignore = ignore
        self._adapter: IProcessAdapter = self._load_adapter(mode)

    def _load_adapter(self, mode):
        from piz_component.kafka.consumer.plugin import SequenceAdapter

        ins = self.load_plugin("classpath", SequenceAdapter(), True)
        adapter = self.cast(ins, IProcessAdapter)
        adapter.set(mode)
        logger.info("subscription data processor initialized,config={}".format(self.get_config()))
        return adapter

    def optimize_kafka_config(self, kafka_config):
        return kafka_config if self._ignore else kafka_config

    def consume_ready(self, consumer, impl, count):
        if consumer and self._ignore:
            impl.begin(count)

    def consume_multi(self, consumer, records, impl):
        offset = self._offset

        class BridgeCls(IBridge):
            def get_id(self):
                return "MD{}".format(len(records))

            def passing(self):
                logger.debug("receive multi data: ".format(len(records)))
                impl.execute(records)
                offset.batch(consumer, records)

        self._adapter.accept(BridgeCls(), self._ignore)

    def consume_single(self, consumer, record, impl):
        offset = self._offset

        class BridgeCls(IBridge):
            def get_id(self):
                return "SD#{}#{}#{}#{}".format(record.topic, record.partition, record.offset, record.timestamp)

            def passing(self):
                logger.debug("receive single data")
                impl.execute(record)
                offset.each(consumer, record)

        self._adapter.accept(BridgeCls(), self._ignore)

    def consume_complete(self, consumer, executor, e=None):
        if e:
            executor.throw_exception(e)
        else:
            executor.end(self._offset)
        self._offset.complete(consumer, e)

    def report(self):
        return self._adapter.report()

    def _log(self, msg, e=None):
        if e and isinstance(e, BaseRuntimeException):
            logger.error(e.get_message())
        else:
            logger.debug(msg)

    def destroy(self, timeout=0):
        self.unload_plugin(self._adapter, timeout)
        logger.info("subscription data processor destroyed,timeout={}".format(timeout))
