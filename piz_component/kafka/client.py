""""""
import logging
import threading
from kafka import KafkaConsumer, KafkaProducer, TopicPartition

from piz_base import AssertUtils, SystemUtils, AbstractException
from piz_component.kafka.consumer.consumer_i import IDataExecutor, IOffsetProcessor
from piz_component.kafka.consumer.processor import DataProcessor
from piz_component.kafka.kafka_e import KafkaException, KafkaCodeEnum
from piz_component.kafka.producer.processor import SenderProcessor
from piz_component.kafka.producer.producer_i import ITransactionProcessor
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

    def initialize(self, config: dict):
        from piz_component.kafka.consumer.plugin import OffsetProcessor

        AssertUtils.assert_type("initialize", config, dict)
        super(Subscription, self).initialize(config)
        # 初始化 IOffsetProcessor
        self._update_config(self.get_convertor().offset_processor_config())
        ins = self.load_plugin("classpath", OffsetProcessor(), True)
        self.offset = self.cast(ins, IOffsetProcessor)
        self.offset.set(self.get_convertor().consumer_mode_value(), self.get_convertor().consumer_ignore_value())
        # 初始化 DataProcessor
        self.processor = DataProcessor(self.offset, self.get_convertor().consumer_mode_value(),
                                       self.get_convertor().consumer_ignore_value())
        self.processor.initialize(self.get_convertor().data_processor_config())
        # 初始化 KafkaConsumer
        kafka_c = self.offset.optimize_kafka_config(self.get_convertor().kafka_config())
        kafka_c = self.processor.optimize_kafka_config(kafka_c)
        self.consumer = KafkaConsumer(**kafka_c)
        logger.info("subscription initialized,config={}".format(config))

    def assign(self, partitions: list, executor: IDataExecutor):
        AssertUtils.assert_type("assign", partitions, dict)
        AssertUtils.assert_type("assign", executor, IDataExecutor)
        self._get_consumer().assign(partitions if partitions else self.get_convertor().assign_config())
        logger.info("subscription:assign")
        self._consume(executor)

    def subscribe(self, executor: IDataExecutor, topics=(), pattern=None, listener=None):
        AssertUtils.assert_type("subscribe", executor, IDataExecutor)
        topics = topics if topics else self.get_convertor().topic_config()

        if not topics:
            pattern = pattern if pattern else self.get_convertor().topic_pattern_config()
        self._get_consumer().subscribe(
            topics=topics,
            pattern=pattern,
            listener=listener)
        msg = "subscription:subscribe,{}".format("topics={}".format(topics) if topics else "pattern={}".format(pattern))
        logger.info(msg)
        self._consume(executor)

    def get_group_id(self):
        return self._get_consumer().get_consumer_group_id() if self._get_consumer() else ""

    def unsubscribe(self):
        self._get_consumer().unsubscribe()
        logger.info("subscription:unsubscribe")

    def _consume(self, executor):
        if not executor:
            raise KafkaException(KafkaCodeEnum.KFK_0009, "data executor null")
        records = None

        while self.loop and self.lock.acquire():
            duration = self.get_convertor().duration_value()
            try:
                records = self._get_consumer().poll(duration)
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
            self.processor.consume_ready(self._get_consumer(), executor)
            try:
                # Python版本修改功能：由于数据结构不同
                data = []
                [data.extend(i) for i in records.values()]
                #
                for item in data:
                    self.processor.consume(self._get_consumer(), item, executor)
                self.processor.consume_complete(self._get_consumer(), executor)
            except KafkaException as e:
                self.processor.consume_complete(self._get_consumer(), executor, e)
                logger.error("consume data:{}".format(e.get_message()))
                raise e

    def _get_consumer(self):
        if not self.consumer:
            raise KafkaException(KafkaCodeEnum.KFK_0010, "consumer not initialize")
        return self.consumer

    def destroy(self, timeout=0):
        if self.consumer and self._is_initialize() and self.loop:
            self.loop = False
            self.unsubscribe()
            super(Subscription, self).destroy(timeout)
            SystemUtils.destroy(self.processor, timeout)
            self.unload_plugin(self.offset, timeout)
            self.consumer.close()
            logger.info("subscription destroyed,timeout={}".format(timeout))


class Production(AbstractClient):
    def __init__(self):
        super(Production, self).__init__()
        self.producer = None
        self.transaction = None
        self.processor = None

    def initialize(self, config: dict):
        from piz_component.kafka.producer.plugin import TransactionProcessor

        AssertUtils.assert_type("initialize", config, dict)
        super(Production, self).initialize(config)
        # 初始化 ITransactionProcessor
        self._update_config(self.get_convertor().transaction_processor_config())
        ins = self.load_plugin("classpath", TransactionProcessor(), True)
        self.transaction = self.cast(ins, ITransactionProcessor)
        self.transaction.set(self.get_convertor().producer_mode_value())
        # 初始化 SenderProcessor
        self.processor = SenderProcessor(self.get_convertor().producer_mode_value())
        self.processor.initialize(self.get_convertor().sender_processor_config())
        # 初始化 KafkaProducer
        kafka_c = self.transaction.optimize_kafka_config(self.get_convertor().kafka_config())
        self.producer = KafkaProducer(**kafka_c)
        self.transaction.init_transactions(self.producer)
        logger.info("production initialized,config={}".format(config))

    def begin_transaction(self):
        try:
            self.transaction.begin_transaction(self._get_producer())
        except KafkaException as e:
            logger.error(e.get_message())
            raise e
        else:
            return self

    def commit_transaction(self, offsets=None, group_id=None):
        try:
            self.transaction.commit_transaction(self._get_producer(), offsets, group_id)
        except KafkaException as e:
            logger.error(e.get_message())
            raise e
        else:
            return self

    def abort_transaction(self):
        try:
            self.transaction.abort_transaction(self._get_producer())
        except KafkaException as e:
            logger.error(e.get_message())
            raise e
        else:
            return self

    def sent(self, record: dict, callback=None):
        AssertUtils.assert_type("sent", record, dict)
        AssertUtils.assert_key_in_dict("sent", record, "topic", "value")
        return self.processor.sent_data(self._get_producer(), record, callback)

    def flush(self):
        self._get_producer().flush()

    def _get_producer(self):
        if not self.producer:
            raise KafkaException(KafkaCodeEnum.KFK_0005, "producer not initialize")
        return self.producer

    def destroy(self, timeout=0):
        if self.producer and self._is_initialize():
            self.flush()
            super(Production, self).destroy(timeout)
            SystemUtils.destroy(self.processor, timeout)
            self.unload_plugin(self.transaction, timeout)
            self.producer.close(timeout)
            logger.info("production destroyed,timeout={}".format(timeout))
