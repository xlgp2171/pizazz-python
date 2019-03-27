""""""
import time


class NumberUtils(object):
    @staticmethod
    def to_int(target, def_value=0):
        if target:
            try:
                return int(target)
            except (TypeError, ValueError):
                pass
        return def_value


class BooleanUtils(object):
    @staticmethod
    def to_boolean(target, def_value=False):
        if target is not None:
            try:
                return "true" == str(target).lower()
            except (TypeError, ValueError):
                pass
        return def_value


class DateUtils(object):
    @staticmethod
    def current_time_millis():
        return int(round(time.time() * 1000))





