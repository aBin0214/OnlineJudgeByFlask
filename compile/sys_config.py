#!/usr/bin/env python
# -*- coding:utf-8 -*-

import yaml
import os
import logging


class Config(object):
    def __init__(self):
        self.file_name = "sys_config.yaml"
        problem_config = self.get_problem_info()
        self.__work_dir = problem_config["work_dir"]  # 代表类的私有属性
        self.__data_dir = problem_config["data_dir"]
        thread_config = self.get_thread_info()
        self.__queue_size = thread_config["queue_size"]
        self.__count_thread = thread_config["count_thread"]

    @property
    def work_dir(self):
        return self.__work_dir

    @property
    def data_dir(self):
        return self.__data_dir

    @property
    def queue_size(self):
        return self.__queue_size

    @property
    def count_thread(self):
        return self.__count_thread

    @staticmethod
    def open_yaml_file(f_name):
        """
        打开yaml格式的文件
        """
        try:
            # 获取当前脚本所在文件夹路径
            cur_path = os.path.dirname(os.path.realpath(__file__))
            # 获取yaml文件路径
            yaml_path = os.path.join(cur_path, f_name)
            # open方法打开直接读出来
            file = open(yaml_path, 'r', encoding='utf-8')
        except FileExistsError as err:
            logger = logging.getLogger("sys_logger")
            logger.error("file open error:" + str(err))
        return file

    def get_mysql_info(self):
        """
        返回mysql的配置信息
        """
        file = Config.open_yaml_file(self.file_name)
        config = yaml.load(file.read(), Loader=yaml.FullLoader)
        return config["mysql_config"]

    def get_problem_info(self):
        """
        获得题目的工作路径和测试数据的路径
        """
        file = Config.open_yaml_file(self.file_name)
        config = yaml.load(file.read(), Loader=yaml.FullLoader)
        return config["problem_config"]

    def get_thread_info(self):
        """
        获得工作队列的相关数量
        """
        file = Config.open_yaml_file(self.file_name)
        config = yaml.load(file.read(), Loader=yaml.FullLoader)
        return config["thread_config"]
