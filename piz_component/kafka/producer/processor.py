""""""
import logging

from piz_base import IPlugin
from piz_component.kafka.kafka_e import KafkaException, KafkaCodeEnum

logger = logging.getLogger(__name__)


class SenderProcessor(IPlugin):
    def __init__(self, mode):
        self.mode = mode

    def sent_data(self, producer, record, callback):
        try:
            # Python版本修改功能：由于方法参数不一致
            tmp = producer.send(**record).add_callback(
                lambda metadata: self._on_completion(metadata, callback)).add_errback(
                lambda set_e: self._on_error(set_e, callback))

            if self.mode.is_sync():
                tmp.get()
            return tmp
        except Exception as e:
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
        logger.error("data send:{}".format(str(e)))

        if callback:
            callback(None, e)
