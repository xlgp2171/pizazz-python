""" 操作系统枚举

"""


class _OSType(object):
    def __init__(self, set_type):
        self.__type = set_type
        self.__bit = None
        self.__version = None

    def get_bit(self):
        return self.__bit

    def get_version(self):
        return self.__version

    def set(self, bit, version):
        self.__bit = bit
        self.__version = version
        return self

    def __str__(self):
        return self.__type

    def __eq__(self, other):
        return self.__type.upper() == str(other).upper()


class OSTypeEnum(object):
    WINDOWS = _OSType("windows")
    LINUX = _OSType("linux")

    @classmethod
    def from_fn(cls, name: str):
        name = str(name).upper()
        return getattr(cls, name, _OSType(str(name)))
