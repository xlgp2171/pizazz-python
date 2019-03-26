""""""


class IObject(object):
    """ 对象接口 """
    def get_id(self):
        return id(self)


class ICloseable(object):
    """ 关闭接口 """
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.destroy(0)

    def destroy(self, timeout=0):
        pass


class IPlugin(IObject, ICloseable):
    """ 插件接口 """
    def initialize(self, config):
        pass


# Python版本接口，用于规范json序列化和反序列化自定义对象
class IJSON(object):
    """JSON的序列化和反序列化接口"""
    @classmethod
    def to_json(cls, target):
        raise NotImplementedError("not supported 'to_json'")

    @classmethod
    def from_json(cls, target):
        raise NotImplementedError("not supported 'from_json'")


class IMessageOutput(ICloseable):
    @classmethod
    def is_enable(cls):
        return False

    def write(self, message):
        raise NotImplementedError("not supported 'write'")

    @classmethod
    def throw_exception(cls, e):
        pass
