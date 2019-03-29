""""""
import threading
import copy

from piz_base.base_i import IPlugin
from piz_base.base_e import AbstractException, ToolException, BasicCodeEnum, AssertException, UtilityException
from piz_base.common.tool_utils import SystemUtils, ClassUtils
from piz_base.common.validate_utils import AssertUtils


class AbstractClassPlugin(IPlugin):
    def __init__(self):
        self.__lock = threading.Lock()
        self.__configure = {}

    def _log(self, msg: str, e=None):
        pass

    def _set_config(self, config: dict):
        if config:
            with self.__lock:
                self.__configure.update(config)
        return self.__configure

    def _update_config(self, config: dict):
        with self.__lock:
            self.__configure.clear()
        self._set_config(config)

    def _get_config(self):
        return self.__configure

    def _copy_config(self):
        return copy.deepcopy(self.__configure)

    @classmethod
    def cast(cls, plugin: IPlugin, clazz):
        AssertUtils.assert_not_null("cast", plugin, clazz)
        return ClassUtils.cast(plugin, clazz)

    def load_plugin(self, key: str, def_plugin=None, initialize=True):
        classpath = self.__configure.get(key, "")
        try:
            return self._load(classpath, key, def_plugin, initialize)
        except (AssertException, UtilityException) as e:
            self._log(e.get_message(), e)
            return self._load("", key, def_plugin, initialize, e)

    def _load(self, classpath, def_class, def_plugin, initialize, e=None):
        if not classpath:
            if def_plugin:
                self._log("load plug-in {}".format(def_plugin.get_id()))
                return self._init_plugin(def_plugin) if initialize else def_plugin
            if not def_class:
                msg = "unable to load plug-in: {}".format(e.get_message() if e else "")
                raise ToolException(BasicCodeEnum.MSG_0014, msg)
            classpath = def_class
        tmp = ClassUtils.new_class(classpath, IPlugin)
        self._log("load plug-in {}".format(tmp.get_id()))
        return self._init_plugin(tmp) if initialize else tmp

    def _init_plugin(self, instance):
        try:
            instance.initialize(self._copy_config())
        except AbstractException as e:
            raise ToolException(BasicCodeEnum.MSG_0020, e.get_message())
        else:
            self._log("initializing plug-in {}".format(instance.get_id()))
            return instance

    def unload_plugin(self, plugin: IPlugin, timeout=0):
        if plugin:
            SystemUtils.destroy(plugin, timeout)
            self._log("unload plug-in {}".format(plugin.get_id()))
