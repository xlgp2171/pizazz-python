""""""
import logging
import threading
from kafka import KafkaConsumer

from piz_base import AssertUtils
from piz_base.base_e import AbstractException
from piz_component.kafka.consumer.consumer_i import IDataExecutor, IOffsetProcessor
from piz_component.kafka.consumer.processor import DataProcessor
from piz_component.kafka.kafka_e import KafkaException, KafkaCodeEnum
from piz_component.kafka.support import AbstractClient

logger = logging.getLogger(__name__)


class Subscription(AbstractClient):
    def __init__(self):
        super(Subscription, self).__init__()
        self.lock = threading.Lock()
        self.loop = True
        self.consumer = None
        self.offset = None
        self.processor = None

    def initialize(self, config):
        from piz_component.kafka.consumer.plugin import OffsetProcessor

        AssertUtils.assert_type("initialize", config, dict)
        super(Subscription, self).initialize(config)
        # 初始化 OffsetProcessor
        self._update_config(self.get_convertor().offset_processor_config())
        ins = self.load_plugin("classpath", OffsetProcessor(), True)
        self.offset = self.cast(ins, IOffsetProcessor)
        self.offset.set(self.get_convertor().consumer_mode_value(), self.get_convertor().consumer_ignore_value())
        # 初始化 processor
        self.processor = DataProcessor(self.offset, self.get_convertor().consumer_mode_value(),
                                       self.get_convertor().consumer_ignore_value())
        self.processor.initialize(self.get_convertor().data_processor_config())
        kafka_c = self.offset.optimize_kafka_config(self.get_convertor().kafka_config())
        kafka_c = self.processor.optimize_kafka_config(kafka_c)
        self.consumer = KafkaConsumer(**kafka_c)
        logger.info("subscription initialized,config={}".format(config))

    def assign(self, partitions, executor):
        AssertUtils.assert_type("assign", partitions, dict)
        AssertUtils.assert_type("assign", executor, IDataExecutor)
        self.get_consumer().assign(partitions if partitions else self.get_convertor().assign_config())
        logger.info("subscription:assign")
        self._consume(executor)

    def subscribe(self, executor, topics=(), pattern=None, listener=None):
        AssertUtils.assert_type("subscribe", executor, IDataExecutor)
        topics = topics if topics else self.get_convertor().topic_config()

        if not topics:
            pattern = pattern if pattern else self.get_convertor().topic_pattern_config()
        self.get_consumer().subscribe(
            topics=topics,
            pattern=pattern,
            listener=listener)
        msg = "subscription:subscribe,{}".format("topics={}".format(topics) if topics else "pattern={}".format(pattern))
        logger.info(msg)
        self._consume(executor)

    def get_group_id(self):
        return self.get_consumer().get_consumer_group_id() if self.get_consumer() else ""

    def unsubscribe(self):
        self.get_consumer().unsubscribe()
        logger.info("subscription:unsubscribe")

    def _consume(self, executor):
        if not executor:
            raise KafkaException(KafkaCodeEnum.KFK_0009, "data executor null")
        records = None

        while self.loop and self.lock.acquire():
            duration = self.get_convertor().duration_value()
            try:
                records = self.get_consumer().poll(duration)
            except AbstractException as e:
                if self.loop:
                    if self.get_convertor().consumer_ignore_value().consume_throwable():
                        msg = "pool data:{} {}"
                        raise KafkaException(KafkaCodeEnum.KFK_0010, msg.format(duration, e.get_message()))

                    logger.error("{} pool data:{}".format(self.loop, e.get_message()))
            finally:
                self.lock.release()
            if not records or not self.loop:
                continue
            self.processor.consume_ready(self.get_consumer(), executor)
            try:
                # Python版本修改功能：由于数据结构不同
                data = []
                [data.extend(i) for i in records.values()]
                #
                for item in data:
                    self.processor.consume(self.get_consumer(), item, executor)
                self.processor.consume_complete(self.get_consumer(), executor)
            except KafkaException as e:
                self.processor.consume_complete(self.get_consumer(), executor, e)
                logger.error("consume data:{}".format(e.get_message()))
                raise e

    def get_consumer(self):
        if not self.consumer:
            raise KafkaException(KafkaCodeEnum.KFK_0010, "consumer not initialize")
        return self.consumer

    def destroy(self, timeout=0):
        if self.consumer and self._is_initialize() and self.loop:
            self.loop = False
            self.unsubscribe()
            super(Subscription, self).destroy(timeout)
            # SystemUtils.destroy(self.processor, timeout)
            # self.unload_plugin(self.offset, timeout)
            self.consumer.close()
            logger.info("subscription destroyed,timeout={}".format(timeout))
