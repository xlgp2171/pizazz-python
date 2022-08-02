""" 响应对象

"""
from piz_base.base_i import IObject


class ResponseObject(IObject):
    SUCCESS = 1
    FAILURE = 0

    def __init__(self, code, message="", properties=None, result=None):
        self._code = code
        self._message = message
        self._result = result
        self._properties = properties if isinstance(properties, dict) else {}

    def get_id(self):
        return str(self._code)

    def is_empty(self):
        return not self._properties and not self._result

    def set_property(self, key: str, target):
        if target:
            self._properties[key] = target

    def get_code(self):
        return self._code

    def get_result(self):
        return self._result

    def get_properties(self):
        return self._properties

    def get_message(self):
        return self._message

    def __str__(self):
        return "{}#{}".format(self._code, self._message if self._message else "")

