""" 环境处理相关

"""

import signal

from collections import OrderedDict


# Python版本类，用于处理运行时程序
class RuntimeContext(object):
    PREFIX = "$sys_#"
    INSTANCE = None

    def __init__(self):
        # shutdown_hook集合，顺序执行
        self._shutdown_hook = OrderedDict()
        self._register_signal()

    def add_shutdown_hook(self, name, fn):
        if isinstance(name, str) and type(fn).__name__ == "function":
            self._shutdown_hook[name] = fn
            return {"name": name, "fn": fn}
        else:
            return None

    def remove_shutdown_hook(self, name):
        if isinstance(name, str) and name in self._shutdown_hook:
            return self._shutdown_hook[name]
        else:
            return None

    # noinspection PyBroadException
    def _call(self, signum, frame):
        for name in self._shutdown_hook.__reversed__():
            if str(name).startswith("$sys_"):
                # 执行系统默认的关闭方法
                if str(name) == RuntimeContext.PREFIX + str(signal.SIGINT):
                    self._shutdown_hook[name](signum, frame)
            else:
                try:
                    self._shutdown_hook[name](signum, frame)
                except Exception:
                    pass

    def _register_signal(self):
        from piz_base.common.enums import OSTypeEnum
        from piz_base.common.tool_utils import SystemUtils
        # ctrl+c 信号
        self._shutdown_hook[RuntimeContext.PREFIX + str(signal.SIGINT)] = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, lambda s, f: self._call(s, f))
        # 非windows信号
        if SystemUtils.LOCAL_OS != OSTypeEnum.WINDOWS:
            # nohup关闭信号
            self._shutdown_hook[RuntimeContext.PREFIX + str(signal.SIGHUP)] = signal.getsignal(signal.SIGHUP)
            signal.signal(signal.SIGHUP, lambda s, f: self._call(s, f))
        # kill pid信号
        self._shutdown_hook[RuntimeContext.PREFIX + str(signal.SIGTERM)] = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGTERM, lambda s, f: self._call(s, f))
