""""""
from kafka.consumer.fetcher import ConsumerRecord

from piz_base import IPlugin, IObject


class IOffsetProcessor(IPlugin):
    def each(self, consumer, record):
        raise NotImplementedError("not supported 'each'")

    def complete(self, consumer, e):
        raise NotImplementedError("not supported 'each'")

    def set(self, mode, ignore):
        raise NotImplementedError("not supported 'set'")

    def get_offset_cache(self):
        raise NotImplementedError("not supported 'get_offset_cache'")

    def rest_offset_committed(self):
        raise NotImplementedError("not supported 'rest_offset_committed'")

    def get_rebalance_listener(self, consumer, listener):
        raise NotImplementedError("not supported 'get_rebalance_listener'")

    def optimize_kafka_config(self, config):
        raise NotImplementedError("not supported 'optimize_kafka_config'")


class IDataExecutor(object):
    def begin(self):
        pass

    def execute(self, record: ConsumerRecord):
        raise NotImplementedError("not supported 'execute'")

    def end(self, offset):
        pass

    def throw_exception(self, e):
        pass


class IProcessAdapter(IPlugin):
    def set(self, mode):
        raise NotImplementedError("not supported 'set'")

    def accept(self, bridge, ignore):
        raise NotImplementedError("not supported 'accept'")

    def monitor(self):
        raise NotImplementedError("not supported 'monitor'")


class IBridge(IObject):
    def passing(self):
        raise NotImplementedError("not supported 'passing'")
