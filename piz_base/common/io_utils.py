""""""
import yaml
import os

from piz_base.common.validate_utils import AssertUtils


class IOUtils(object):
    @staticmethod
    def get_resource_as_stream(resource, mode='r'):
        AssertUtils.assert_not_null("get_resource_as_stream", resource)
        return open(
            resource,
            mode=mode)


class YAMLUtils(object):
    @staticmethod
    def from_yaml(resource):
        with IOUtils.get_resource_as_stream(resource) as f:
            return yaml.safe_load(f.read())


class PathUtils(object):
    @staticmethod
    def to_file_path(path, *paths):
        path = os.path.dirname(os.path.realpath(path))
        return os.path.join(path, *paths)

