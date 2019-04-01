""""""
import sys
import os
import platform
import importlib
import ctypes
import inspect
import uuid

from piz_base.context import RuntimeContext
from piz_base.base_i import ICloseable
from piz_base.base_e import UtilityException, BasicCodeEnum
from piz_base.common.enum import OSTypeEnum
from piz_base.common.validate_utils import AssertUtils


class SystemUtils(object):
    LOCAL_ENCODING = None
    LOCAL_OS = None
    LOCAL_DIR = None

    @staticmethod
    def get_local_encoding():
        def_e = sys.getdefaultencoding()
        return os.getenv("piz.encoding", def_e)

    @staticmethod
    def get_local_os():
        name = platform.system()
        bit = platform.architecture()[0]
        version = platform.platform()
        return OSTypeEnum.from_fn(name).set(bit, version)

    @staticmethod
    def destroy(target: ICloseable, timeout=0):
        if isinstance(target, ICloseable):
            try:
                target.destroy(timeout)
            except Exception:
                pass

    @staticmethod
    def add_shutdown_hook(closeable: ICloseable, timeout=0, name=None):
        if isinstance(closeable, ICloseable):
            name = name if isinstance(name, str) else SystemUtils.new_uuid()
            return RuntimeContext.INSTANCE.add_shutdown_hook(name, lambda signum, frame: closeable.destroy(timeout))
        else:
            return None

    @staticmethod
    def new_uuid():
        return str(uuid.uuid1())

    @staticmethod
    def new_uuid_simple():
        return SystemUtils.new_uuid().replace("-", "")

    # Python版本方法，用于结束线程
    @staticmethod
    def async_raise(tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)

        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

        if res == 0:
            pass
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")


class ClassUtils(object):
    @staticmethod
    def cast(target, set_type):
        if not set_type:
            return None
        AssertUtils.assert_not_null("cast", target)

        if not isinstance(target, set_type):
            msg = "class {} needs to implement class or interface {}".format(target, set_type)
            raise UtilityException(BasicCodeEnum.MSG_0004, msg)

        return target

    @staticmethod
    def new_class(classpath: str, set_type, name=None):
        cls = ClassUtils.load_class(classpath, name)
        return ClassUtils.new_and_cast(cls, set_type)

    @staticmethod
    def load_class(classpath: str, name=None):
        AssertUtils.assert_not_null("load_class", classpath)
        pkg = None
        m_name = classpath
        c_name = name

        if not name:
            path = str(classpath).rsplit(".", 1)
            c_name = path[-1]
            m_name = path[0]
        # path = str(classpath).rsplit(".", 1 if name else 2)
        #
        # if not name and len(path) < 2:
        #     msg = "{} is not a valid path(e.g. [pkg.]module.Class)".format(classpath)
        #     raise AssertException(BasicCodeEnum.MSG_0005, msg)
        # c_name = name if name else path[-1]
        # m_name = path[-1] if name else path[-2]
        # pkg = path[0] if (name and len(path) > 1) or (not name and len(path) > 2) else None
        module = importlib.import_module(
            m_name,
            package=pkg)
        return getattr(module, c_name)

    @staticmethod
    def new_and_cast(clazz, set_type):
        if not set_type:
            return None
        AssertUtils.assert_not_null("new_and_cast", clazz)
        return ClassUtils.cast(clazz(), set_type)
