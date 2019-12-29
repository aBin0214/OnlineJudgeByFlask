#!/usr/bin/env python
# coding=utf-8

import os
import sys_config
import logging


def clean_work_dir(solution_id):
    """
    清理word目录，删除临时文件
    :param solution_id:
    :return:
    """
    # dir_name = os.path.join(config.work_dir, str(solution_id))
    # shutil.rmtree(dir_name)
    pass


def get_data_count(problem_id):
    """
    获得测试数据的个数信息
    """
    cfg = sys_config.Config()
    full_path = os.path.join(cfg.data_dir, str(problem_id))
    try:
        files = os.listdir(full_path)
    except OSError as e:
        logger = logging.getLogger("sys_logger")
        logger.error(e)
        return 0
    count = 0
    for item in files:
        if item.endswith(".in") and item.startswith("data"):
            count += 1
    return count


if __name__ == '__main__':
    get_data_count(1)
