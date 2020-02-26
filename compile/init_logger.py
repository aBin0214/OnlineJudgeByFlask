#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging.handlers
import os
import time


def make_dir(make_dir_path):
    path = make_dir_path.strip()
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def init_logger(name):
    """
    初始化logger
    :param name:
    :return:
    """
    logger = logging.getLogger(name)

    stream_handler = logging.StreamHandler()

    log_dir_name = "logs"
    make_dir(log_dir_name)
    log_file_name = 'backstage-' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.log'
    log_file_str = log_dir_name + os.sep + log_file_name
    file_handler = logging.FileHandler(log_file_str, encoding='UTF-8')

    logger.setLevel(logging.INFO)
    stream_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s : %(message)s")
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

