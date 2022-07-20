""""""
import logging
import threading
from kafka import KafkaConsumer, KafkaProducer

from piz_base import ValidateUtils, SystemUtils
from piz_component.kafka.consumer.consumer_i import IOffsetProcessor, IDataRecord, IMultiDataExecutor
from piz_component.kafka.consumer.processor import DataProcessor
from piz_component.kafka.kafka_e import KafkaException, KafkaCodeEnum
from piz_component.kafka.producer.processor import SenderProcessor
from piz_component.kafka.producer.producer_i import ITransactionProcessor
from piz_component.kafka.core import AbstractClient

logger = logging.getLogger(__name__)


class Subscription(AbstractClient):
    def __init__(self, configure):
        super(Subscription, self).__init__(configure)
        self._lock = threading.Lock()
        self._loop = True
        self._consumer = None
        self._offset = None
        self._processor = None

    def initialize(self):
        from piz_component.kafka.consumer.plugin import OffsetProcessor
        # 初始化 IOffsetProcessor
        self._update_config(self.get_convertor().offset_processor_config())
        ins = self.load_plugin("classpath", OffsetProcessor(), True)
        self._offset = self.cast(ins, IOffsetProcessor)
        self._offset.set(self.get_convertor().consumer_mode_value(), self.get_convertor().consumer_ignore_value())
        # 数据处理类
        self._processor = DataProcessor(
            self._offset, self.get_convertor().consumer_mode_value(), self.get_convertor().consumer_ignore_value(),
            self.get_convertor().data_processor_config())
        # 创建Kafka消费类
        kafka_c = self._offset.optimize_kafka_config(self.get_convertor().kafka_config())
        self._consumer = KafkaConsumer(**self._processor.optimize_kafka_config(kafka_c))
        logger.info("subscription initialized,config={}".format(self.get_convertor().get_target_config()))

    def assign(self, partitions: list, impl: IDataRecord):
        ValidateUtils.is_type("assign", partitions, list)
        ValidateUtils.is_type("assign", impl, IMultiDataExecutor)
        self._consumer.assign(partitions if partitions else self.get_convertor().assign_config())
        logger.info("subscription:assign")
        self._consume(impl)

    def subscribe(self, impl: IDataRecord, topics=(), pattern=None, listener=None):
        ValidateUtils.is_type("subscribe", impl, IMultiDataExecutor)
        topics = topics if topics else self.get_convertor().topic_config()

        if not topics:
            pattern = pattern if pattern else self.get_convertor().topic_pattern_config()
        self._consumer.subscribe(
            topics=topics,
            pattern=pattern,
            listener=listener)
        msg = "subscription:subscribe,{}".format("topics={}".format(topics) if topics else "pattern={}".format(pattern))
        logger.info(msg)
        self._consume(impl)

    def get_group_id(self):
        return self._consumer.get_consumer_group_id() if self._consumer else ""

    def unsubscribe(self):
        self._loop = False

        with self._lock:
            self._consumer.unsubscribe()
        logger.info("subscription:unsubscribe")

    def _consume(self, impl):
        ValidateUtils.not_null("_consume", impl)
        self._loop = True
        records = None

        while self._loop and self._lock.acquire():
            duration = self.get_convertor().duration_value()
            try:
                records = self._consumer.poll(duration)
            except Exception as e:
                if self._loop:
                    logger.error("{} pool data:{}".format(self._loop, str(e)))

                    if self.get_convertor().consumer_ignore_value().consume_throwable():
                        self._loop = False
                        msg = "pool data:{} {}"
                        raise KafkaException(KafkaCodeEnum.KFK_0010, msg.format(duration, str(e)))
            finally:
                self._lock.release()

            has_record = records and len(records) > 0
            self._processor.consume_ready(self._consumer, impl, len(records) if has_record else 0)
            try:
                if has_record and self._loop:
                    # Python版本修改功能：由于数据结构不同
                    result = []
                    [result.extend(i) for i in records.values()]
                    #
                    self._processor.consume_multi(self._consumer, result, impl)
                self._processor.consume_complete(self._consumer, impl)
            except KafkaException as e:
                self._processor.consume_complete(self._consumer, impl, e)
                logger.error("consume data:{}".format(e.get_message()))

                if self.get_convertor().consumer_ignore_value().consume_throwable():
                    self._loop = False
                    raise e

    def get_target(self):
        return self._consumer

    def destroy(self, timeout=0):
        if self._consumer and self._loop:
            self._loop = False
            self.unsubscribe()
            super(Subscription, self).destroy(timeout)
            SystemUtils.destroy(self._processor, timeout)
            self.unload_plugin(self._offset, timeout)
            self._consumer.close()
            logger.info("subscription destroyed,timeout={}".format(timeout))


class Production(AbstractClient):
    def __init__(self, configure):
        super(Production, self).__init__(configure)
        self._producer = None
        self._transaction = None
        self._processor = None

    def initialize(self):
        from piz_component.kafka.producer.plugin import TransactionProcessor
        # 获取发布事务配置
        self._update_config(self.get_convertor().transaction_processor_config())
        # 构建事务处理器
        ins = self.load_plugin("classpath", TransactionProcessor(), True)
        self._transaction = self.cast(ins, ITransactionProcessor)
        self._transaction.set(self.get_convertor().producer_mode_value())
        # 构建发送消息处理组件
        self._processor = SenderProcessor(self.get_convertor().producer_mode_value(),
                                          self.get_convertor().sender_processor_config())
        # 构建kafka发送实例
        kafka_c = self._transaction.optimize_kafka_config(self.get_convertor().kafka_config())
        self._producer = KafkaProducer(**kafka_c)
        self._transaction.init_transactions(self._producer)
        logger.info("production initialized,config={}".format(self.get_convertor().get_target_config()))

    def sent(self, record: dict, callback=None):
        ValidateUtils.is_type("sent", record, dict)
        ValidateUtils.is_key_in_dict("sent", record, "topic", "value")
        return self._processor.sent_data(self._producer, record, callback)

    def flush(self):
        self._producer.flush()

    def get_target(self):
        return self._producer

    def destroy(self, timeout=0):
        if self._producer:
            self.flush()
            super(Production, self).destroy(timeout)
            self.unload_plugin(self._transaction, timeout)
            self._producer.close(timeout)
            logger.info("production destroyed,timeout={}".format(timeout))
