""""""
import yaml
import uri
import os
import json

from urllib import parse

from uri import URI

from piz_base.common.tool_utils import SystemUtils
from piz_base.base_e import AssertException, UtilityException, BasicCodeEnum
from piz_base.common.validate_utils import AssertUtils


class IOUtils(object):
    @staticmethod
    def get_resource_as_stream(resource, mode='r'):
        AssertUtils.assert_not_null("get_resource_as_stream", resource)
        try:
            return open(
                resource,
                mode=mode)
        except FileNotFoundError as e:
            raise UtilityException(BasicCodeEnum.MSG_0003, "unable to read file {} because: {}".format(resource, e))


class YAMLUtils(object):
    @staticmethod
    def from_yaml(resource):
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
    def to_file_path(path, *paths):
        path = os.path.dirname(os.path.realpath(path))
        return os.path.join(path, *paths)

    @staticmethod
    def to_uri(set_uri):
        AssertUtils.assert_not_null("to_uri", set_uri)
        uri_p = URI(set_uri)
        return uri_p if uri_p.scheme else URI(
            schema="string",
            path=set_uri)

    @staticmethod
    def resolve(set_uri, target):
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
