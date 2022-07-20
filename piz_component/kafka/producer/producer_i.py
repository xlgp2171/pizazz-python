""" 发布接口

"""
from piz_base import IPlugin


class ITransactionProcessor(IPlugin):
    def init_transactions(self, producer):
        raise NotImplementedError("not supported 'init_transactions'")

    def begin_transaction(self, producer):
        raise NotImplementedError("not supported 'begin_transaction'")

    def commit_transaction(self, producer, offsets, group_id):
        raise NotImplementedError("not supported 'commit_transaction'")

    def abort_transaction(self, producer):
        raise NotImplementedError("not supported 'abort_transaction'")

    def set(self, mode):
        raise NotImplementedError("not supported 'set'")

    def optimize_kafka_config(self, config):
        raise NotImplementedError("not supported 'optimize_kafka_config'")
