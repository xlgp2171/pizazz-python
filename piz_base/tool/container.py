""""""
import threading
import os
import sys
from concurrent import futures
from concurrent.futures import TimeoutError

from piz_base.context import RuntimeContext
from piz_base.base_e import AbstractException
from piz_base.common.tool_utils import SystemUtils
from piz_base.common.type_utils import NumberUtils

from piz_base.base_i import IPlugin, IMessageOutput


class AbstractContainer(IPlugin):
    def __init__(self, plugin: IPlugin, output: IMessageOutput):
        self._properties = {}
        self._plugin = plugin
        self._output = output
        self._event = threading.Event()

    def __callable(self, timeout):
        try:
            self._plugin.destroy(timeout)
        except Exception as e:
            self._output.throw_exception(e)
            return -1
        else:
            return 0

    def log(self, msg, e=None):
        raise NotImplementedError("not supported 'log'")

    def wait_for_shutdown(self):
        self._event.wait()

    def wakeup(self):
        self._event.set()

    def initialize(self, config):
        self._properties["timeout"] = os.getenv("piz.sc.timeout", 30000)

    def destroy(self, timeout=0):
        if not timeout or timeout < 0:
            timeout = NumberUtils.to_int(self._properties["timeout"], 20000)
            timeout = timeout if timeout < 60000 else 20000
        if timeout == 0:
            msg = "immediate container destruction"
            print(msg)
            self.log(msg)
            status = self.__callable(0)
        else:
            msg = "container destroyed in {}ms".format(timeout)
            print(msg)
            self.log(msg)
            try:
                status = futures.ThreadPoolExecutor(1).submit(lambda: self.__callable(timeout)).result(timeout / 1000)
            except TimeoutError as e:
                msg = "container cannot stop within {}ms".format(timeout)
                print(msg)
                self.log(msg, e)
                status = -2
            except Exception as e:
                status = -3
                print(e)
                self._output.throw_exception(e)
                # 强制退出
                os._exit(status)
            finally:
                SystemUtils.destroy(self._output)

        if status != -3:
            sys.exit(status)


class SocketContainer(AbstractContainer):
    def __init__(self, plugin: IPlugin, config: dict, output: IMessageOutput):
        super(SocketContainer, self).__init__(plugin, output)
        try:
            self.initialize(config)
        except AbstractException as e:
            self._output.throw_exception(e)
        self.__socket = None
        self.__hook = None
        self.__command = None
        self.__closed = False
        self.__lock = threading.Lock()

    def initialize(self, config: dict):
        super(SocketContainer, self).initialize(config)
        host = config.get("host", "")
        port = NumberUtils.to_int(config.get("port", -1))
        key = config.get("key", "")
        cmd_len = config.get("cmd.len", -1)
        self._properties["$host"] = host if host and isinstance(host, str) else os.getenv("piz.sc.host", "")
        self._properties["$port"] = port if isinstance(port, int) and port != -1 else os.getenv("piz.sc.port", 14134)
        self._properties["$key"] = key if key and isinstance(key, str) else os.getenv(
            "piz.sc.key", SystemUtils.new_uuid_simple())
        self._properties["$cmd.len"] = cmd_len if isinstance(cmd_len, int) and cmd_len != -1 else os.getenv(
            "piz.sc.cmd.len", 36)

    def get_id(self):
        return self.__class__.__name__

    def wait_for_shutdown(self):
        self.__hook = SystemUtils.add_shutdown_hook(self)
        port = self._properties.get("$port", -1)

        if port <= 0:
            if self._output.is_enable():
                self._output.write("container holding...")
            super(SocketContainer, self).wait_for_shutdown()
        else:
            self._socket_waiting(port)
            SystemUtils.destroy(self, -1)

    def _socket_waiting(self, port):
        # TODO 暂时没有实现socket组件
        raise AbstractException("TODO", ":(")

    def _command(self, data):
        if self.__command:
            try:
                self.__command.write(data)
            except Exception as e:
                self._output.throw_exception(e)

        return data

    def set_command(self, command):
        self.__command = command
        return self

    def log(self, msg, e=None):
        if self._output.is_enable():
            self._output.write(msg)

    def destroy(self, timeout=0):
        with self.__lock:
            if not self.__closed:
                self.__closed = True

                if self.__hook:
                    RuntimeContext.INSTANCE.remove_shutdown_hook(self.__hook.get("name", "null"))
                super(SocketContainer, self).destroy(timeout)
