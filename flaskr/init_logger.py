#!/usr/bin/env python
# -*- coding:utf-8 -*-


from flask.logging import default_handler
import logging
import os
import time


def make_dir(make_dir_path):
    path = make_dir_path.strip()
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def init_logger():
    """
    初始化全局的日志
    :return:
    """
    log_dir_name = "logs"
    make_dir(log_dir_name)
    log_file_name = 'page-' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
    log_file_str = log_dir_name + os.sep + log_file_name
    log_level = logging.WARNING
    logger_format = \
        logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s : %(message)s")

    handler = logging.FileHandler(log_file_str, encoding='UTF-8')
    handler.setLevel(log_level)
    handler.setFormatter(logger_format)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logger_format)

    root = logging.getLogger()
    root.removeHandler(default_handler)
    root.addHandler(handler)
    root.addHandler(stream_handler)


