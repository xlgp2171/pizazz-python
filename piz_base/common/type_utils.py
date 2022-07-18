""" 类型转换辅助类

"""

import time
from datetime import datetime

from piz_base.common.validate_utils import ValidateUtils
from piz_base.base_e import BasicCodeEnum, IllegalException
from dateutil.relativedelta import relativedelta


class NumberUtils(object):
    @staticmethod
    def to_int(target, def_value=0):
        if target:
            try:
                return int(target)
            except (TypeError, ValueError):
                pass
        return def_value

    @staticmethod
    def to_float(target, def_value=0.0):
        if target:
            try:
                return float(target)
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
    STANDARD_PATTERN = "%Y-%m-%d %H:%M:%S"

    # Python版本方法，类似System.currentTimeMillis()
    @staticmethod
    def current_time_millis():
        return int(round(time.time() * 1000))

    @staticmethod
    def parse(time_str: str, pattern: str = STANDARD_PATTERN):
        ValidateUtils.not_null("parse", time_str, pattern)
        try:
            return datetime.strptime(time_str, pattern)
        except ValueError:
            raise IllegalException(BasicCodeEnum.MSG_0017,
                                   "cannot parse datetime {} as format {}".format(time_str, pattern))

    @staticmethod
    def format(date: datetime, pattern: str = STANDARD_PATTERN):
        ValidateUtils.not_null("format", date, pattern)
        return date.strftime(pattern)

    @staticmethod
    def add_days(date: datetime, amount: int = 1):
        if not date:
            date = datetime.now()
        return date + relativedelta(days=amount)

    @staticmethod
    def add_months(date: datetime, amount: int = 1):
        if not date:
            date = datetime.now()
        return date + relativedelta(months=amount)

    @staticmethod
    def add_seconds(date: datetime, amount: int = 1):
        if not date:
            date = datetime.now()
        return date + relativedelta(seconds=amount)

    @staticmethod
    def add_minutes(date: datetime, amount: int = 1):
        if not date:
            date = datetime.now()
        return date + relativedelta(minutes=amount)
