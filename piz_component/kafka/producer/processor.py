""" 发送具体实现

"""
import logging
import traceback

from piz_component.kafka.kafka_e import KafkaException, KafkaCodeEnum

logger = logging.getLogger(__name__)


class SenderProcessor(object):
    def __init__(self, mode, config):
        self._mode = mode

    def sent_data(self, producer, record, callback):
        try:
            # Python版本修改功能：由于方法参数不一致
            tmp = producer.send(**record).add_callback(
                lambda metadata: self._on_completion(metadata, callback)).add_errback(
                lambda set_e: self._on_error(set_e, callback))

            if self._mode.is_sync():
                tmp.get()
            return tmp
        except Exception as e:
            logger.error(traceback.format_exc(limit=10))
            raise KafkaException(KafkaCodeEnum.KFK_0012, "data send:{}".format(str(e)))

    # Python版本修改功能：由于方法参数不一致
    @classmethod
    def _on_completion(cls, metadata, callback):
        logger.debug("data send:{}".format(metadata))

        if callback:
            callback(metadata, None)

    # Python版本修改功能：由于方法参数不一致
    @classmethod
    def _on_error(cls, e, callback):
        logger.error("data send:{}".format(traceback.format_exc(limit=20)))

        if callback:
            callback(None, e)
