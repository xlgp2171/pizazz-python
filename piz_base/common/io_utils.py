""" 输入输出辅助类

"""

import yaml
import os
import json
import tempfile

from piz_base.base_e import UtilityException, BasicCodeEnum, IllegalException
from piz_base.common.validate_utils import ValidateUtils


class IOUtils(object):
    @staticmethod
    def get_resource_as_stream(resource: str, mode='r', **args):
        ValidateUtils.not_null("get_resource_as_stream", resource)
        try:
            return open(
                resource,
                mode=mode, **args)
        except FileNotFoundError as e:
            raise UtilityException(BasicCodeEnum.MSG_0003, "unable to read file {} because: {}".format(resource, e))


class YAMLUtils(object):
    @staticmethod
    def from_yaml(resource: str, **args):
        with IOUtils.get_resource_as_stream(resource, **args) as f:
            try:
                return yaml.safe_load(f.read())
            except Exception as e:
                raise UtilityException(BasicCodeEnum.MSG_0013, "yaml could not parse because:{}".format(e))

    @staticmethod
    def to_yaml(resource: str, data: dict, **args):
        with IOUtils.get_resource_as_stream(
                resource,
                mode='w', **args) as f:
            try:
                return yaml.safe_dump(data, f)
            except Exception as e:
                raise UtilityException(BasicCodeEnum.MSG_0013, "yaml could not to file because:{}".format(e))


class JSONUtils(object):
    @staticmethod
    def to_json(target, encode=None):
        try:
            return json.dumps(
                target,
                default=encode)
        except Exception as e:
            raise IllegalException(BasicCodeEnum.MSG_0013, "json could not parse because: {}".format(e))

    @staticmethod
    def from_json(target, decode=None, clazz=None):
        try:
            tmp = json.loads(
                target,
                object_hook=decode)
        except Exception as e:
            raise IllegalException(BasicCodeEnum.MSG_0013, "json could not parse because: {}".format(e))

        if clazz and tmp:
            obj = clazz()
            obj.__dict__ = tmp
            return obj

        return tmp


class PathUtils(object):
    @staticmethod
    def to_byte_array(path: str):
        ValidateUtils.not_null("to_byte_array", path)
        try:
            with open(
                    file=path,
                    mode='rb') as f:
                return f.read()
        except Exception as e:
            msg = "unable to read file {} because: {}".format(path, e)
            raise UtilityException(BasicCodeEnum.MSG_0003, msg)

    @staticmethod
    def delete(path: str, deep=True):
        ValidateUtils.not_null("delete", path)

        if os.path.isdir(path):
            if deep:
                PathUtils._delete_directory(path)
                PathUtils._delete(path, True)
        else:
            PathUtils._delete(path, False)

    @staticmethod
    def _delete_directory(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                PathUtils._delete(os.path.join(root, name), False)
            for name in dirs:
                PathUtils._delete(os.path.join(root, name), True)

    # Python版本方法，用于删除文件或文件夹
    # noinspection PyBroadException
    @staticmethod
    def _delete(path, is_dir):
        try:
            if is_dir:
                os.rmdir(path)
            else:
                os.remove(path)
            return True
        except Exception:
            return False

    # noinspection PyTypeChecker
    @staticmethod
    def copy_to_path(data: bytes, path: str, mode="wb", replace=True):
        ValidateUtils.not_null("copy_to_path", path, data)

        if replace and os.path.exists(path):
            PathUtils.delete(path, False)
        try:
            with open(path, mode) as out:
                out.write(data)
                return len(data)
        except Exception as e:
            msg = "unable to create file {} because: {}".format(path, e)
            raise UtilityException(BasicCodeEnum.MSG_0003, msg)

    @staticmethod
    def copy_to_temp(data: bytes, prefix: str, call_fn=None):
        ValidateUtils.not_null("copy_to_temp", data)
        delete = True if call_fn else False

        with tempfile.NamedTemporaryFile(
                prefix=prefix,
                suffix=".tmp",
                delete=delete) as temp:
            temp.write(data)

            if call_fn:
                call_fn(temp.name, data)
            return temp.name

    @staticmethod
    def walk_paths(path: str, set_filter=None, include_dir=False):
        ValidateUtils.not_null("list_paths", path)

        def def_filter_fn(target):
            return True if target else False

        set_filter = def_filter_fn if not set_filter else set_filter

        def loop_fn(arr, set_root, args):
            for i in args:
                target = os.path.join(set_root, i)

                if set_filter(target):
                    arr.append(target)
        tmp = []

        for root, dirs, files in os.walk(path):
            if include_dir:
                loop_fn(tmp, root, dirs)
            loop_fn(tmp, root, files)

        return tmp

    # Python版本方法，用于追加path
    @staticmethod
    def to_file_path(path: str, *paths: str):
        path = os.path.dirname(os.path.realpath(path)) if path else ""
        path = os.path.join(path, *paths)
        return os.path.realpath(path)

    # Python版本方法，用于获取文件夹名称
    @staticmethod
    def get_parent_name(path: str):
        dir_name = os.path.dirname(path)
        return os.path.basename(dir_name)
