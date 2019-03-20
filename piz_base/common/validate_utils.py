""""""


from piz_base.base_e import BasicCodeEnum, AssertException


class AssertUtils(object):
    @staticmethod
    def assert_not_null(method, *args):
        if args:
            for i, arg in enumerate(args):
                if not arg:
                    msg = "the {} input parameter of the target '{}' is null".format(i + 1, method)
                    raise AssertException(BasicCodeEnum.MSG_0001, msg)

    @staticmethod
    def assert_type(method, target, set_type):
        AssertUtils.assert_not_null(method, target, set_type)

        if not isinstance(target, set_type):
            msg = "the target needs to implement {} from target '{}'".format(set_type, method)
            raise AssertException(BasicCodeEnum.MSG_0005, msg)

    @staticmethod
    def assert_key_in_dict(method, config, *keys):
        AssertUtils.assert_not_null(method, config, *keys)

        if not isinstance(config, dict):
            msg = "the target must be 'dict' type from  target '{}'".format(method)
            raise AssertException(BasicCodeEnum.MSG_0005, msg)
        for k in keys:
            if k not in config:
                msg = "the key '{}' not in dict from target '{}'".format(k, method)
                raise AssertException(BasicCodeEnum.MSG_0005, msg)
