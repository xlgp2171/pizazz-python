""" 序列化工具类

"""
from kafka.serializer.abstract import Deserializer
from kafka.serializer.abstract import Serializer


class StringSerializer(Serializer):
    def __init__(self, **config):
        super(StringSerializer, self).__init__()
        self._encoding = "UTF-8"

        if config and "serializer_encoding" in config:
            self._encoding = config.get("serializer_encoding", self._encoding)

    def serialize(self, topic, value):
        return "" if value is None else bytes(value, self._encoding)


class StringDeserializer(Deserializer):
    def __init__(self, **config):
        super(StringDeserializer, self).__init__()
        self._encoding = "UTF-8"

        if config and "deserializer_encoding" in config:
            self._encoding = config.get("deserializer_encoding", self._encoding)

    def deserialize(self, topic, value):
        return "" if value is None else str(value, self._encoding)
