""" 发布枚举

"""
from piz_component.kafka import helper
from piz_base import PathUtils, YAMLUtils
from piz_component.kafka.kafka_e import KafkaCodeEnum, KafkaException


class _ProducerMode(object):
    def __init__(self, name, sync, transaction):
        self.__name = name
        self.__sync = sync
        self.__transaction = transaction

    def is_sync(self):
        return self.__sync

    def is_transaction(self):
        return self.__transaction

    def __str__(self):
        return self.__name


class ProducerModeEnum(object):
    # 异步事务发送
    ASYNC_TRANSACTION = _ProducerMode("ASYNC_TRANSACTION", False, True)
    # 同步事务发送
    SYNC_TRANSACTION = _ProducerMode("SYNC_TRANSACTION", True, True)
    # 异步发送
    ASYNC = _ProducerMode("ASYNC", False, False)
    # 同步发送
    SYNC = _ProducerMode("SYNC", True, False)

    @classmethod
    def from_fn(cls, mode):
        mode = str(mode).upper()

        if not hasattr(cls, mode):
            raise KafkaException(KafkaCodeEnum.KFK_0011, mode)
        return getattr(cls, mode)


class _ProducerTemplate(object):
    def __init__(self, name):
        self.__name = name
        self.__resource = PathUtils.to_file_path(__file__, "../", "resource", "{}.yml")

    def fill(self, client_c, config_c):
        if self.__name != ProducerTemplateEnum.NONE.__name:
            config = YAMLUtils.from_yaml(str(self.__resource).format(self.__name.lower()))
            helper.merge(config, "client", client_c)
            helper.merge(config, "config", config_c)
        return client_c, config_c


class ProducerTemplateEnum(object):
    # 高效
    PRODUCER_EFFICIENCY = _ProducerTemplate("PRODUCER_EFFICIENCY")
    # 标准
    PRODUCER_NORMAL = _ProducerTemplate("PRODUCER_NORMAL")
    # 事务
    PRODUCER_TRANSACTION = _ProducerTemplate("PRODUCER_TRANSACTION")
    # 无
    NONE = _ProducerTemplate("NONE")

    @classmethod
    def from_fn(cls, template):
        template = str(template).upper()
        return getattr(cls, template, ProducerTemplateEnum.NONE)
