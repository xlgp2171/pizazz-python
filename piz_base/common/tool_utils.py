""""""
import importlib

from piz_base.base_i import ICloseable
from piz_base.base_e import UtilityException, BasicCodeEnum
from piz_base.common.validate_utils import AssertUtils


class SystemUtils(object):
    @staticmethod
    def destroy(target, timeout=0):
        if isinstance(target, ICloseable):
            try:
                target.destroy(timeout)
            except Exception:
                pass


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
    def new_class(classpath, set_type, name=None):
        cls = ClassUtils.load_class(classpath, name)
        return ClassUtils.new_and_cast(cls, set_type)

    @staticmethod
    def load_class(classpath, name=None):
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
