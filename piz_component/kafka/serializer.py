""""""
from kafka.serializer.abstract import Deserializer
from kafka.serializer.abstract import Serializer


class StringSerializer(Serializer):
    def __init__(self, **config):
        self.encoding = "UTF-8"

        if config and "serializer_encoding" in config:
            self.encoding = config.get("serializer_encoding", self.encoding)

    def serialize(self, topic, value):
        return None if not value else bytes(value, self.encoding)


class StringDeserializer(Deserializer):
    def __init__(self, **config):
        self.encoding = "UTF-8"

        if config and "deserializer_encoding" in config:
            self.encoding = config.get("deserializer_encoding", self.encoding)

    def deserialize(self, topic, value):
        return None if not value else str(value, self.encoding)
