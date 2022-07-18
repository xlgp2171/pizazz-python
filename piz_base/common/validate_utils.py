""" 验证工具

"""


from piz_base.base_e import BasicCodeEnum, ValidateException


class ValidateUtils(object):
    @staticmethod
    def not_null(method: str, *args):
        if args:
            for i, arg in enumerate(args):
                if not arg:
                    msg = "the {} input parameter of the target '{}' is null".format(i + 1, method)
                    raise ValidateException(BasicCodeEnum.MSG_0001, msg)

    @staticmethod
    def is_type(method: str, target, set_type):
        ValidateUtils.not_null(method, target, set_type)

        if not isinstance(target, set_type):
            msg = "the target needs to implement {} from target '{}'".format(set_type, method)
            raise ValidateException(BasicCodeEnum.MSG_0005, msg)

    @staticmethod
    def is_key_in_dict(method: str, config, *keys):
        ValidateUtils.not_null(method, config, *keys)

        if not isinstance(config, dict):
            msg = "the target must be 'dict' type from  target '{}'".format(method)
            raise ValidateException(BasicCodeEnum.MSG_0005, msg)
        for k in keys:
            if k not in config:
                msg = "the key '{}' not in dict from target '{}'".format(k, method)
                raise ValidateException(BasicCodeEnum.MSG_0005, msg)
