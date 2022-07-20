""" 类加载器工具

"""

import threading
import copy

from piz_base.base_i import IPlugin, IObject
from piz_base.base_e import ToolException, BasicCodeEnum, ValidateException, UtilityException, BaseRuntimeException
from piz_base.common.tool_utils import SystemUtils, ClassUtils
from piz_base.common.validate_utils import ValidateUtils


class AbstractClassPlugin(IObject):
    def __init__(self, configure=None):
        self._lock = threading.Lock()
        self._configure = configure if isinstance(configure, dict) else {}

    def _log(self, msg: str, e=None):
        pass

    def _set_config(self, config: dict):
        if config:
            with self._lock:
                self._configure.update(config)
        return self._configure

    def _update_config(self, config: dict):
        with self._lock:
            self._configure.clear()
        self._set_config(config)

    def get_config(self):
        return self._configure

    # Python版本方法，用于复制配置
    def _copy_config(self):
        return copy.deepcopy(self._configure)

    @classmethod
    def cast(cls, plugin: IPlugin, clazz):
        ValidateUtils.not_null("cast", plugin, clazz)
        return ClassUtils.cast(plugin, clazz)

    def load_plugin(self, key: str, def_plugin=None, initialize=True):
        classpath = self._configure.get(key, "")
        try:
            return self._load(classpath, key, def_plugin, initialize)
        except (ValidateException, UtilityException) as e:
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
        except BaseRuntimeException as e:
            raise ToolException(BasicCodeEnum.MSG_0020, e.get_message())
        else:
            self._log("initializing plug-in {}".format(instance.get_id()))
            return instance

    def unload_plugin(self, plugin: IPlugin, timeout=0):
        if plugin:
            SystemUtils.destroy(plugin, timeout)
            self._log("unload plug-in {}".format(plugin.get_id()))
