""""""
import yaml
import uri
import os
import json
import tempfile

from urllib import parse

from uri import URI

from piz_base.common.tool_utils import SystemUtils
from piz_base.base_e import AssertException, UtilityException, BasicCodeEnum
from piz_base.common.validate_utils import AssertUtils


class IOUtils(object):
    @staticmethod
    def get_resource_as_stream(resource: str, mode='r'):
        AssertUtils.assert_not_null("get_resource_as_stream", resource)
        try:
            return open(
                resource,
                mode=mode)
        except FileNotFoundError as e:
            raise UtilityException(BasicCodeEnum.MSG_0003, "unable to read file {} because: {}".format(resource, e))


class YAMLUtils(object):
    @staticmethod
    def from_yaml(resource: str):
        with IOUtils.get_resource_as_stream(resource) as f:
            try:
                return yaml.safe_load(f.read())
            except Exception as e:
                raise UtilityException(BasicCodeEnum.MSG_0013, "yaml could not parse because:{}".format(e))


class JSONUtils(object):
    @staticmethod
    def to_json(target, encode=None):
        return json.dumps(
            target,
            default=encode)

    @staticmethod
    def from_json(target, decode=None, clazz=None):
        tmp = json.loads(
            target,
            object_hook=decode)

        if clazz and tmp:
            obj = clazz()
            obj.__dict__ = tmp
            return obj

        return tmp


class PathUtils(object):
    @staticmethod
    def to_byte_array(path: str):
        AssertUtils.assert_not_null("to_byte_array", path)
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
        AssertUtils.assert_not_null("delete", path)

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

    @staticmethod
    def copy_to_path(path: str, set_in, mode="wb", replace=True):
        AssertUtils.assert_not_null("copy_to_path", path, set_in)

        if replace and os.path.exists(path):
            PathUtils.delete(path, False)
        try:
            with open(path, mode) as out:
                data = set_in.read()
                out.write(data)
                return len(data)
        except Exception as e:
            msg = "unable to create file {} because: {}".format(path, e)
            raise UtilityException(BasicCodeEnum.MSG_0003, msg)
        finally:
            set_in.close()

    @staticmethod
    def copy_to_temp(data: bytes, prefix: str, call_fn=None):
        AssertUtils.assert_not_null("copy_to_temp", data)
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
    def list_paths(path: str, set_filter=None, include_dir=False):
        AssertUtils.assert_not_null("list_paths", path)

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

    # 该方法若在windows下，无法正确解析参数为file://C:/tmp/user的path
    # 需要自行修改为file:///C:/tmp/user，或者采用scheme传参方式"C:/tmp/user", "file"
    @staticmethod
    def to_uri(set_uri: str, scheme=None):
        AssertUtils.assert_not_null("to_uri", set_uri)

        if scheme:
            if not set_uri.startswith("/"):
                set_uri = "/" + set_uri
            uri_p = URI(
                scheme=scheme,
                path=set_uri.replace(" ", "%20"))
        else:
            uri_p = URI(set_uri.replace(" ", "%20"))
        return uri_p if uri_p.scheme else URI(
            scheme="string",
            path=set_uri.replace(" ", "%20"))

    @staticmethod
    def resolve(set_uri: URI, target: str):
        try:
            uri_s = str(set_uri)
            set_uri = PathUtils.to_uri(uri_s + ("" if uri_s.endswith("/") else "/"))
        except AssertException:
            return uri
        else:
            target = parse.quote(
                target,
                encoding=SystemUtils.LOCAL_ENCODING)
            return set_uri.resolve(target.replace("+", "%20").replace("%21", "!").replace("%27", "'").replace(
                "%28", "(").replace("%29", ")").replace("%7E", "~"))

    # Python版本方法，用于从URI转换
    @staticmethod
    def from_uri(set_uri: URI):
        if not set_uri.scheme or set_uri.scheme != "file":
            raise UtilityException(BasicCodeEnum.MSG_0005, "URI scheme is not 'file'")
        if set_uri.fragment:
            raise UtilityException(BasicCodeEnum.MSG_0005, "URI has a fragment component")
        if set_uri.query:
            raise UtilityException(BasicCodeEnum.MSG_0005, "URI has a query component")
        path = str(set_uri.path)

        if not path:
            raise UtilityException(BasicCodeEnum.MSG_0005, "URI path component is empty")
        if len(path) > 2 and path[2] == ':':
            path = path[1:]
        return parse.unquote(path)

    # Python版本方法，用于追加path
    @staticmethod
    def to_file_path(path: str, *paths: str):
        path = os.path.dirname(os.path.realpath(path))
        return os.path.join(path, *paths)
