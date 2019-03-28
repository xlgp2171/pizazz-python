""""""
import signal

from collections import OrderedDict


# Python版本类，用于处理运行时程序
class RuntimeContext(object):
    INSTANCE = None

    def __init__(self):
        # shutdown_hook集合，顺序执行
        self.__shutdown_hook = OrderedDict()
        self._register_signal()

    def add_shutdown_hook(self, name, fn):
        if isinstance(name, str) and type(fn).__name__ == "function":
            self.__shutdown_hook[name] = fn
            return {"name": name, "fn": fn}
        else:
            return None

    def remove_shutdown_hook(self, name):
        if isinstance(name, str) and name in self.__shutdown_hook:
            return self.__shutdown_hook[name]
        else:
            return None

    def __call(self, signum, frame):
        for name in self.__shutdown_hook.__reversed__():
            if str(name).startswith("$sys_"):
                # 执行系统默认的关闭方法
                if str(name) == "$sys_#" + str(signal.SIGINT):
                    self.__shutdown_hook[name](signum, frame)
            else:
                try:
                    self.__shutdown_hook[name](signum, frame)
                except Exception:
                    pass

    def _register_signal(self):
        from piz_base.common.enum import OSTypeEnum
        from piz_base.common.tool_utils import SystemUtils
        # ctrl+c 信号
        self.__shutdown_hook["$sys_#" + str(signal.SIGINT)] = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, lambda s, f: self.__call(s, f))
        # 非windows信号
        if SystemUtils.LOCAL_OS != OSTypeEnum.WINDOWS:
            # nohup关闭信号
            self.__shutdown_hook["$sys_#" + str(signal.SIGHUP)] = signal.getsignal(signal.SIGHUP)
            signal.signal(signal.SIGHUP, lambda s, f: self.__call(s, f))
        # kill pid信号
        self.__shutdown_hook["$sys_#" + str(signal.SIGTERM)] = signal.getsignal(signal.SIGTERM)
        signal.signal(signal.SIGTERM, lambda s, f: self.__call(s, f))
