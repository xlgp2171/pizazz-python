""""""


from piz_base.base_e import BasicCodeEnum, AssertException


class AssertUtils(object):
    @staticmethod
    def assert_not_null(method, *args):
        if args:
            for i, arg in enumerate(args):
                if not arg:
                    msg = "the {} input parameter of the target {} is null".format(i + 1, method)
                    raise AssertException(BasicCodeEnum.MSG_0001, msg)

    @staticmethod
    def assert_type(method, target, set_type):
        AssertUtils.assert_not_null(method, target, set_type)

        if not isinstance(target, set_type):
            msg = "the target type needs to be {}".format(set_type)
            raise AssertException(BasicCodeEnum.MSG_0005, msg)


