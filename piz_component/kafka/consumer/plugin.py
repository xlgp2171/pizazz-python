""""""
import logging
import threading
import copy

from kafka.consumer.subscription_state import ConsumerRebalanceListener
from kafka.structs import OffsetAndMetadata, TopicPartition
from kafka.serializer.abstract import Deserializer

from piz_base import BooleanUtils, ClassUtils, JSONUtils
from piz_component.kafka.consumer.enum import ConsumerModeEnum, KafkaCodeEnum
from piz_component.kafka.consumer.consumer_i import IProcessAdapter, IOffsetProcessor
from piz_component.kafka.kafka_e import KafkaException

logger = logging.getLogger(__name__)


class SequenceAdapter(IProcessAdapter):
    def __init__(self):
        self.__mode = None

    def initialize(self, config):
        logger.info("adapter SequenceAdapter initialized,config={}".format(config))

    def set(self, mode):
        if not hasattr(ConsumerModeEnum, str(mode)):
            raise KafkaException(KafkaCodeEnum.KFK_0001, "adapter not support:{}".format(mode))
        self.__mode = mode

    def accept(self, bridge, ignore):
        try:
            bridge.passing()
            logger.debug("consume:{}".format(bridge.get_id()))
        except KafkaException as e:
            raise e
        except Exception as e:
            if ignore.consume_throwable():
                msg = "consume:{} {}".format(bridge.get_id(), str(e))
                raise KafkaException(KafkaCodeEnum.KFK_0010, msg)
            else:
                logger.warning("consume:{} {}".format(bridge.get_id(), str(e)))

    def monitor(self):
        return JSONUtils.to_json({"STATUS": "activate", "MODE": str(self.__mode), "ADAPTER": str(self.__class__)})

    def destroy(self, timeout=0):
        logger.info("adapter SequenceAdapter destroyed,timeout={}".format(timeout))


class OffsetProcessor(IOffsetProcessor):
    def __init__(self):
        # {TopicPartition: OffsetAndMetadata}
        self._offset_committed = {}
        # {TopicPartition: OffsetAndMetadata}
        self._offset_cache = {}
        self.__mode = None
        self.__ignore = None
        self.__lock = threading.Lock()

    def _callback(self, offsets, e):
        if e and isinstance(e, Exception):
            logger.error("consumer commit:{} {}".format(offsets, str(e)))
        elif offsets:
            self.__make_committed(offsets)

    def __offset_commit(self, consumer, force):
        # {TopicPartition: OffsetAndMetadata}
        tmp = self.get_offset_cache()

        if self.__mode.is_sync() or force:
            try:
                if self.__mode.is_each() and not force:
                    if tmp:
                        consumer.commit(tmp)
                else:
                    consumer.commit()
            except Exception as e:
                if self.__ignore.offset_throwable():
                    raise KafkaException(KafkaCodeEnum.KFK_0006, "consumer commit:{} {}".format(tmp, str(e)))
                else:
                    logger.warning("consumer commit:{} {}".format(tmp, str(e)))
                    return
            else:
                self.__make_committed(tmp)
        elif self.__mode.is_each():
            consumer.commit_async(tmp, lambda offset, set_e: self._callback(offset, set_e))
        else:
            consumer.commit_async(
                callback=lambda offset, set_e: self._callback(offset, set_e))
        logger.debug("consumer commit:{}".format(tmp))

    def __make_committed(self, offsets):
        with self.__lock:
            for k, v in offsets.items():
                if k in self._offset_committed:
                    if v.offset > self._offset_committed.get(k).offset:
                        self._offset_committed[k] = v
                else:
                    self._offset_committed[k] = v
        logger.debug("consumer mark committid:{}".format(offsets))

    def each(self, consumer, record):
        # tp = {"topic": record.topic, "partition": record.partition}
        tp = TopicPartition(record.topic, record.partition)

        if tp in self._offset_committed:
            if record.offset > self._offset_committed.get(tp).offset:
                self.__set_and_commit(consumer, record, tp)
            logger.debug("{} consumed:{}".format(tp, record.offset))
        else:
            self.__set_and_commit(consumer, record, tp)

    def __set_and_commit(self, consumer, record, tp):
        with self.__lock:
            # self.offset_cache[tp] = {"offset": record.offset, "leaderEpoch": None, "metadata": ""}
            self._offset_cache[tp] = OffsetAndMetadata(record.offset, "")

        if self.__mode != ConsumerModeEnum.MANUAL_NONE_NONE and not self.__mode.is_auto() and self.__mode.is_each():
            self.__offset_commit(consumer, False)

    def complete(self, consumer, e):
        if self.__mode != ConsumerModeEnum.MANUAL_NONE_NONE and not self.__mode.is_auto() and not e:
            self.__offset_commit(consumer, False)
            logger.debug("consumer commit sync:{}".format(self.__mode.is_sync()))

    def optimize_kafka_config(self, config):
        commit_mode = True if not self.__mode else self.__mode.is_auto()

        if "enable_auto_commit" not in config or (
                self.__mode and commit_mode != BooleanUtils.to_boolean(config["enable_auto_commit"], True)):
            config["enable_auto_commit"] = commit_mode
            logger.info("set subscription config:enable_auto_commit={},mode={}".format(commit_mode, self.__mode))
        if "group_id" not in config or not config["group_id"]:
            config["group_id"] = "pizazz"
            logger.info("set subscription config:group_id=pizazz")
        # Python版本新增功能：实例化KEY反序列化类
        if "key_deserializer" in config and isinstance(config["key_deserializer"], str):
            config["key_deserializer"] = ClassUtils.new_class(config["key_deserializer"], Deserializer)
            logger.info("set subscription config:key_deserializer={}".format(config["key_deserializer"]))
        # Python版本新增功能：实例化VALUE反序列化类
        if "value_deserializer" in config and isinstance(config["value_deserializer"], str):
            config["value_deserializer"] = ClassUtils.new_class(config["value_deserializer"], Deserializer)
            logger.info("set subscription config:value_deserializer={}".format(config["value_deserializer"]))

        return config

    def get_rebalance_listener(self, consumer, listener):
        mode = self.__mode
        lock = self.__lock
        offset_cache = self._offset_cache
        offset_commit_fn = self.__offset_commit
        rest_offset_committed_fn = self.rest_offset_committed

        class ListenerCls(ConsumerRebalanceListener):
            def on_partitions_revoked(self, revoked):
                if mode != ConsumerModeEnum.MANUAL_NONE_NONE and not mode.is_auto() and not mode.is_each():
                    try:
                        offset_commit_fn(consumer, True)
                    except KafkaException as e:
                        logger.error(e.get_message())
                if listener:
                    listener.on_partitions_revoked(revoked)
                logger.info("subscription partitions revoked:{}".format(revoked))

            def on_partitions_assigned(self, assigned):
                rest_offset_committed_fn()
                with lock:
                    offset_cache.clear()
                if listener:
                    listener.on_partitions_assigned(assigned)
                logger.info("subscription partitions assigned:{}".format(assigned))

        return ListenerCls()

    def get_offset_cache(self):
        with self.__lock:
            return copy.copy(self._offset_cache)

    def rest_offset_committed(self):
        with self.__lock:
            self._offset_committed.clear()

    def set(self, mode, ignore):
        self.__mode = mode
        self.__ignore = ignore

    def destroy(self, timeout=0):
        self.rest_offset_committed()
        self._offset_cache.clear()
        logger.info("subscription offset processor destroyed,timeout={}".format(timeout))
