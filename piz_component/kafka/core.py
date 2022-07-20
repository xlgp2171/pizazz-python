""" 核心辅助类

"""
import logging

from kafka.partitioner import DefaultPartitioner
from kafka.structs import TopicPartition

from piz_base.base_e import BaseRuntimeException
from piz_component.kafka import helper as hr
from piz_base import BasicCodeEnum, ICloseable, SystemUtils, NumberUtils, AbstractClassPlugin, ValidateUtils
from piz_component.kafka.consumer.enum import ConsumerTemplateEnum, ConsumerModeEnum, ConsumerIgnoreEnum
from piz_component.kafka.kafka_e import KafkaException, KafkaCodeEnum
from piz_component.kafka.producer.enum import ProducerTemplateEnum, ProducerModeEnum

logger = logging.getLogger(__name__)


class AbstractClient(AbstractClassPlugin):
    def __init__(self, configure):
        super(AbstractClient, self).__init__(configure)
        # 创建配置类
        self._convertor = ConfigConvertor(self.get_config())
        # 直接初始化
        self.initialize()

    def initialize(self):
        raise NotImplementedError("not supported 'initialize'")

    def get_convertor(self):
        return self._convertor

    def _log(self, msg, e=None):
        if e and isinstance(e, BaseRuntimeException):
            logger.error(e.get_message())
        else:
            logger.debug(msg)

    def destroy(self, timeout=0):
        SystemUtils.destroy(self._convertor, timeout)


class ConfigConvertor(ICloseable):
    def __init__(self, config):
        ValidateUtils.not_null("ConfigConvertor", config)
        self._config = {}
        self._template = None
        self._parse(config)

    def _parse(self, config):
        if not isinstance(config, dict) and len(config) == 0:
            raise KafkaException(BasicCodeEnum.MSG_0005, "base config invalid")
        client_c = config.get("client", {})
        client_c = client_c if client_c else {}
        config_c = config.get("config", {})
        config_c = config_c if config_c else {}
        self._template = config.get("template", "")
        self._try_use_template(client_c, config_c)
        self._config = {"client": client_c, "config": config_c}

    def _try_use_template(self, client_c, config_c):
        if self._template:
            ProducerTemplateEnum.from_fn(self._template).fill(client_c, config_c)
            ConsumerTemplateEnum.from_fn(self._template).fill(client_c, config_c)

    def get_template(self):
        return self._template

    def _get_config_nested(self, key, def_value):
        return hr.get_nested(self._config, def_value, "config", key)

    def _get_client_nested(self, key, def_value):
        return hr.get_nested(self._config, def_value, "client", key)

    def offset_processor_config(self):
        return self._get_config_nested("offset-processor", {})

    def transaction_processor_config(self):
        return self._get_config_nested("transaction-processor", {})

    def data_processor_config(self):
        return self._get_config_nested("data-processor", {})

    def sender_processor_config(self):
        return self._get_config_nested("sender-processor", {})

    def duration_value(self):
        value = self._get_config_nested("duration", "")
        return NumberUtils.to_int(value, 10000)

    def consumer_mode_value(self):
        value = self._get_config_nested("mode", "")
        return ConsumerModeEnum.from_fn(value)

    def producer_mode_value(self):
        value = self._get_config_nested("mode", "")
        return ProducerModeEnum.from_fn(value)

    def consumer_ignore_value(self):
        value = self._get_config_nested("ignore", "")

        if value:
            try:
                return ConsumerIgnoreEnum.from_fn(value)
            except KafkaException:
                pass
        return ConsumerIgnoreEnum.NONE

    def kafka_config(self):
        return self._config.get("client", {})

    def get_consumer_group_id(self):
        return self._get_client_nested("group_id", "demo")

    def assign_config(self):
        config = self._get_config_nested("topic-partition", ())

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
        value = self._get_config_nested("topic-pattern", "")

        if not value:
            raise KafkaException(KafkaCodeEnum.KFK_0004, "config 'topicPattern' null")
        return value

    def topic_config(self):
        value = self._get_config_nested("topic", [])
        return list(value)

    def get_target_config(self):
        return self._config.copy()

    def destroy(self, timeout=0):
        self._config.clear()


class RandomPartitioner(DefaultPartitioner):
    @classmethod
    def __call__(cls, key, all_partitions, available):
        return super(RandomPartitioner, cls).__call__(None, all_partitions, available)
