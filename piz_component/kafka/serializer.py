""""""
from kafka.serializer.abstract import Deserializer
from kafka.serializer.abstract import Serializer


class StringSerializer(Serializer):
    def __init__(self, **config):
        super(StringSerializer, self).__init__()
        self.__encoding = "UTF-8"

        if config and "serializer_encoding" in config:
            self.__encoding = config.get("serializer_encoding", self.__encoding)

    def serialize(self, topic, value):
        return None if value is None else bytes(value, self.__encoding)


class StringDeserializer(Deserializer):
    def __init__(self, **config):
        super(StringDeserializer, self).__init__()
        self.__encoding = "UTF-8"

        if config and "deserializer_encoding" in config:
            self.__encoding = config.get("deserializer_encoding", self.__encoding)

    def deserialize(self, topic, value):
        return None if value is None else str(value, self.__encoding)
