""""""
import logging

from kafka.partitioner import DefaultPartitioner
from kafka.structs import TopicPartition

import piz_component.kafka.helper as hr
from piz_base import (BasicCodeEnum, AbstractException, ICloseable, SystemUtils, NumberUtils, AssertUtils,
                      AbstractClassPlugin)
from piz_component.kafka.consumer.enum import ConsumerTemplateEnum, ConsumerModeEnum, ConsumerIgnoreEnum
from piz_component.kafka.kafka_e import KafkaException, KafkaCodeEnum
from piz_component.kafka.producer.enum import ProducerTemplateEnum, ProducerModeEnum

logger = logging.getLogger(__name__)


class AbstractClient(AbstractClassPlugin):
    def __init__(self):
        super(AbstractClient, self).__init__()
        self.__initialized = False
        self.__convertor = None

    def initialize(self, config):
        if self.__initialized:
            raise KafkaException(BasicCodeEnum.MSG_0020, "client initialized")
        else:
            self.__initialized = True
        self.__convertor = ConfigConvertor(config)

    def get_convertor(self):
        return self.__convertor

    def _is_initialize(self):
        return self.__initialized

    def _log(self, msg, e=None):
        if e and isinstance(e, AbstractException):
            logger.error(e.get_message())
        else:
            logger.debug(msg)

    def destroy(self, timeout=0):
        if self.__initialized:
            SystemUtils.destroy(self.__convertor, timeout)


class ConfigConvertor(ICloseable):
    def __init__(self, config):
        AssertUtils.assert_not_null("ConfigConvertor", config)
        self.__config = {}
        self.__template = None
        self.__parse(config)

    def __parse(self, config):
        if not isinstance(config, dict) and len(config) == 0:
            raise KafkaException(BasicCodeEnum.MSG_0005, "base config invalid")
        client_c = config.get("client", {})
        client_c = client_c if client_c else {}
        config_c = config.get("config", {})
        config_c = config_c if config_c else {}
        self.__template = config.get("template", "")
        self.__try_use_template(client_c, config_c)
        self.__config = {"client": client_c, "config": config_c}

    def __try_use_template(self, client_c, config_c):
        if self.__template:
            ProducerTemplateEnum.from_fn(self.__template).fill(client_c, config_c)
            ConsumerTemplateEnum.from_fn(self.__template).fill(client_c, config_c)

    def get_template(self):
        return self.__template

    def __get_config_nested(self, key, def_value):
        return hr.get_nested(self.__config, def_value, "config", key)

    def __get_client_nested(self, key, def_value):
        return hr.get_nested(self.__config, def_value, "client", key)

    def offset_processor_config(self):
        return self.__get_config_nested("offsetProcessor", {})

    def transaction_processor_config(self):
        return self.__get_config_nested("transactionProcessor", {})

    def data_processor_config(self):
        return self.__get_config_nested("dataProcessor", {})

    def sender_processor_config(self):
        return self.__get_config_nested("senderProcessor", {})

    def duration_value(self):
        value = self.__get_config_nested("duration", "")
        return NumberUtils.to_int(value, 10000)

    def consumer_mode_value(self):
        value = self.__get_config_nested("mode", "")
        return ConsumerModeEnum.from_fn(value)

    def producer_mode_value(self):
        value = self.__get_config_nested("mode", "")
        return ProducerModeEnum.from_fn(value)

    def consumer_ignore_value(self):
        value = self.__get_config_nested("ignore", "")

        if value:
            try:
                return ConsumerIgnoreEnum.from_fn(value)
            except AbstractException:
                pass
        return ConsumerIgnoreEnum.NONE

    def kafka_config(self):
        return self.__config.get("client", {})

    def get_consumer_group_id(self):
        return self.__get_client_nested("group_id", "pizazz")

    def assign_config(self):
        config = self.__get_config_nested("topicPartition", ())

        if not config:
            raise KafkaException(KafkaCodeEnum.KFK_0002, "config 'topicPartition' null")
        tp = []

        for item in config:
            partitions = str(item).split("#")

            if len(partitions) < 2:
                raise KafkaException(KafkaCodeEnum.KFK_0003, "topic partition format:T#[NUM]#[NUM]")
            for i, partition in enumerate(partitions):
                if i == 0:
                    continue
                partition = NumberUtils.to_int(partition, -1)

                if partition < 0:
                    raise KafkaException(KafkaCodeEnum.KFK_0003, "partition format:[NUM]")
                tp.append(TopicPartition(partitions[0], partition))
                # tp.append({"topic": partitions[0], "partition": partition})

        return tp

    def topic_pattern_config(self):
        value = self.__get_config_nested("topicPattern", "")

        if not value:
            raise KafkaException(KafkaCodeEnum.KFK_0004, "config 'topicPattern' null")
        return value

    def topic_config(self):
        value = self.__get_config_nested("topic", [])
        return list(value)

    def destroy(self, timeout=0):
        self.__config.clear()


class RandomPartitioner(DefaultPartitioner):
    @classmethod
    def __call__(cls, key, all_partitions, available):
        return super(RandomPartitioner, cls).__call__(None, all_partitions, available)
