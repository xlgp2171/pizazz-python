""""""
import piz_component.kafka.helper as hr
from piz_base import YAMLUtils, PathUtils
from piz_component.kafka.kafka_e import KafkaException, KafkaCodeEnum


class _ConsumerIgnore(object):
    def __init__(self, name, offset, consume):
        self.__name = name
        self.__offset = offset
        self.__consume = consume

    def offset_throwable(self):
        return self.__offset

    def consume_throwable(self):
        return self.__consume

    def __str__(self):
        return self.__name


class ConsumerIgnoreEnum(object):
    # 忽略offset和consume异常
    OFFSET_CONSUME = _ConsumerIgnore("OFFSET_CONSUME", False, False)
    # 忽略consume异常
    CONSUME = _ConsumerIgnore("CONSUME", False, True)
    # 忽略offset异常
    OFFSET = _ConsumerIgnore("OFFSET", True, False)
    # 无任何忽略
    NONE = _ConsumerIgnore("NONE", True, True)

    @classmethod
    def from_fn(cls, ignore):
        ignore = str(ignore).upper()
        return getattr(cls, ignore, ConsumerIgnoreEnum.NONE)


class _ConsumerMode(object):
    def __init__(self, name, auto, sync, each):
        self.__name = name
        self.__auto = auto
        self.__sync = sync
        self.__each = each

    def is_auto(self):
        return self.__auto

    def is_sync(self):
        return self.__sync

    def is_each(self):
        return self.__each

    def __str__(self):
        return self.__name


class ConsumerModeEnum(object):
    # 自动异步一轮
    AUTO_ASYNC_ROUND = _ConsumerMode("AUTO_ASYNC_ROUND", True, False, False)
    # 手动异步每个
    MANUAL_ASYNC_EACH = _ConsumerMode("MANUAL_ASYNC_EACH", False, False, True)
    # 手动同步每个
    MANUAL_SYNC_EACH = _ConsumerMode("MANUAL_SYNC_EACH", False, True, True)
    # 手动异步一轮
    MANUAL_ASYNC_ROUND = _ConsumerMode("MANUAL_ASYNC_ROUND", False, False, False)
    # 手动同步一轮
    MANUAL_SYNC_ROUND = _ConsumerMode("MANUAL_SYNC_ROUND", False, True, False)
    # 手动无提交
    MANUAL_NONE_NONE = _ConsumerMode("MANUAL_NONE_NONE", False, False, False)

    @classmethod
    def from_fn(cls, mode):
        mode = str(mode).upper()

        if not hasattr(cls, mode):
            raise KafkaException(KafkaCodeEnum.KFK_0007, mode)
        return getattr(cls, mode)


class _ConsumerTemplate(object):
    def __init__(self, name):
        self.__name = name
        self.__resource = PathUtils.to_file_path(__file__, "../", "resource", "{}.yml")

    def fill(self, client_c, config_c):
        if self.__name != ConsumerTemplateEnum.NONE.__name:
            config = YAMLUtils.from_yaml(str(self.__resource).format(self.__name.lower()))
            hr.merge(config, "client", client_c)
            hr.merge(config, "config", config_c)
        return client_c, config_c


class ConsumerTemplateEnum(object):
    # 高效
    CONSUMER_EFFICIENCY = _ConsumerTemplate("CONSUMER_EFFICIENCY")
    # 标准
    CONSUMER_NORMAL = _ConsumerTemplate("CONSUMER_NORMAL")
    # 可靠
    CONSUMER_RELIABILITY = _ConsumerTemplate("CONSUMER_RELIABILITY")
    # 无
    NONE = _ConsumerTemplate("NONE")

    @classmethod
    def from_fn(cls, template):
        template = str(template).upper()
        return getattr(cls, template, ConsumerTemplateEnum.NONE)
