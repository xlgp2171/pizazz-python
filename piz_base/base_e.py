""""""


class BasicCodeEnum(object):
    #  预留
    MSG_0000 = "MSG0000#"
    # 空指针异常：NullPointException
    MSG_0001 = "MSG0001#"
    # 安全异常：SecurityException
    MSG_0002 = "MSG0002#"
    # 输入输出异常：IOException
    MSG_0003 = "MSG0003#"
    # 类转换异常：ClassCastException
    MSG_0004 = "MSG0004#"
    # 非法参数异常：IllegalArgumentException
    MSG_0005 = "MSG0005#"
    # 调用目标异常：InvocationTargetException
    MSG_0006 = "MSG0006#"
    # 非法使用异常：IllegalAccessException
    MSG_0007 = "MSG0007#"
    # 实例化异常：InstantiationException
    MSG_0008 = "MSG0008#"
    # 类无法找到异常：ClassNotFoundException
    MSG_0009 = "MSG0009#"
    # 反射异常：ReflectException
    MSG_0010 = "MSG0010#"
    # 注册异常：RegistryException
    MSG_0011 = "MSG0011#"
    # 中断异常：InterruptedException
    MSG_0012 = "MSG0012#"
    # 序列化异常：SerializationException
    MSG_0013 = "MSG0013#"
    # 插件异常：PluginException
    MSG_0014 = "MSG0014#"
    # 加密解密异常：CryptoException
    MSG_0015 = "MSG0015#"
    # 套接字异常：SocketException
    MSG_0016 = "MSG0016#"
    # 日期时间异常：DateException
    MSG_0017 = "MSG0017#"
    # XML异常：XMLException
    MSG_0018 = "MSG0018#"
    # 日志异常：LogException
    MSG_0019 = "MSG0019#"
    # 初始化异常：InitializeException
    MSG_0020 = "MSG0020#"
    # 数据库异常：DatabaseException
    MSG_0021 = "MSG0021#"
    # 编译异常：CompileException
    MSG_0022 = "MSG0022#"
    # 参数无法找到异常: ArgumentNotFoundException
    MSG_0023 = "MSG0023#"


class AbstractException(Exception):
    """ 异常超类 """
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def get_message(self):
        return "{}{}".format(self.code, self.msg)

    def __str__(self):
        return self.get_message()


class AssertException(AbstractException):
    """ 断言异常 """
    def __init__(self, code, msg):
        super(AssertException, self).__init__(code, msg)


class UtilityException(AbstractException):
    """ 通用工具异常 """
    def __init__(self, code, msg):
        super(UtilityException, self).__init__(code, msg)


class ToolException(AbstractException):
    """ 通用组件异常 """
    def __init__(self, code, msg):
        super(ToolException, self).__init__(code, msg)
