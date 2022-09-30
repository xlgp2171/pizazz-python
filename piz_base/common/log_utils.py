import logging
import os
from logging.handlers import RotatingFileHandler

_levelToName = {
    logging.ERROR: 'ERROR',
    logging.WARNING: 'WARNING',
    logging.INFO: 'INFO',
    logging.DEBUG: 'DEBUG'
}


def level_to_name(level):
    result = _levelToName.get(level, "")
    return result if result else "NOTSET"


class _RotatingFileHandler(RotatingFileHandler, logging.StreamHandler):
    def __init__(self, log_name, level, project_path="", max_bytes=20*1024*1024, backup_count=10):
        _filename = os.path.join(project_path, "logs", f"{log_name}_{level_to_name(level)}.log")
        super().__init__(filename=_filename, maxBytes=max_bytes, backupCount=backup_count)


# noinspection PyArgumentList
def logging_set_up(log_tag="", project_path="", level=logging.INFO, log_format="%(asctime)s %(message)s", **kwargs):
    if log_tag:
        handlers = [_RotatingFileHandler(log_tag, level, project_path, **kwargs)]
    else:
        handlers = [logging.StreamHandler()]
    logging.basicConfig(
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        level=level,
        handlers=handlers
    )
