""" 事务实现

"""
import logging

from kafka.serializer.abstract import Serializer
from kafka.partitioner import DefaultPartitioner
from kafka.version import __version__

from piz_base import ClassUtils
from piz_component.kafka.kafka_e import KafkaException, KafkaCodeEnum
from piz_component.kafka.producer.producer_i import ITransactionProcessor

logger = logging.getLogger(__name__)


class TransactionProcessor(ITransactionProcessor):
    def __init__(self):
        self.__mode = None

    def init_transactions(self, producer):
        if self.__mode.is_transaction():
            # Python版本不支持producer.init_transactions方法
            raise KafkaException(KafkaCodeEnum.KFK_0015, "{} not supported 'init_transactions'".format(__version__))

    def begin_transaction(self, producer):
        if self.__mode.is_transaction():
            # Python版本不支持producer.begin_transaction方法
            raise KafkaException(KafkaCodeEnum.KFK_0015, "{} not supported 'begin_transaction'".format(__version__))

    def commit_transaction(self, producer, offsets, group_id):
        if self.__mode.is_transaction():
            # Python版本不支持producer.commit_transaction方法
            raise KafkaException(KafkaCodeEnum.KFK_0015, "{} not supported 'commit_transaction'".format(__version__))

    def abort_transaction(self, producer):
        if self.__mode.is_transaction():
            # Python版本不支持producer.abort_transaction方法
            raise KafkaException(KafkaCodeEnum.KFK_0015, "{} not supported 'abort_transaction'".format(__version__))

    def set(self, mode):
        self.__mode = mode

    def optimize_kafka_config(self, config):
        transaction_mode = False if not self.__mode else self.__mode.is_transaction()

        if transaction_mode and "transactional_id" not in config:
            config["transactional_id"] = "pizazz"
            logger.info("set production config:transactional_id=pizazz,mode={}".format(self.__mode))
        # Python版本新增功能：实例化KEY序列化类
        if "key_serializer" in config and isinstance(config["key_serializer"], str):
            config["key_serializer"] = ClassUtils.new_class(config["key_serializer"], Serializer)
            logger.info("set production config:key_serializer={}".format(config["key_serializer"]))
        # Python版本新增功能：实例化VALUE反序列化类
        if "value_serializer" in config and isinstance(config["value_serializer"], str):
            config["value_serializer"] = ClassUtils.new_class(config["value_serializer"], Serializer)
            logger.info("set production config:value_serializer={}".format(config["value_serializer"]))
        # Python版本新增功能：实例化PARTITION选择器类
        if "partitioner" in config and isinstance(config["partitioner"], str):
            config["partitioner"] = ClassUtils.new_class(config["partitioner"], DefaultPartitioner)
            logger.info("set production config:partitioner={}".format(config["partitioner"]))

        return config
