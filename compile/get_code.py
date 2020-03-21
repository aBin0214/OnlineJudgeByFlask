#!/usr/bin/env python
# coding=utf-8

import os
import logging

from compile import mysql_DBUtils
from compile import sys_config


def get_code(solution_id, pro_lang):
    """
    从数据库获取代码并写入work目录下对应的文件
    :param solution_id:
    :param pro_lang:
    :return:
    """
    file_name = {
        "gcc": "main.c",
        "g++": "main.cpp",
        "java": "Main.java",
        'ruby': "main.rb",
        "perl": "main.pl",
        "pascal": "main.pas",
        "go": "main.go",
        "lua": "main.lua",
        'python2': 'main.py',
        'python3': 'main.py',
        "haskell": "main.hs"
    }
    select_code_sql = "select submit_content from solution where id_solution = {} limit 1;"

    mysql = mysql_DBUtils.MyPyMysqlPool()
    result = mysql.get_one(select_code_sql.format(solution_id))
    logger = logging.getLogger("sys_logger")
    if result is not None and result is not False:
        code = result["submit_content"]
    else:
        logger.error("cannot get code of run_id {}".format(solution_id))
        return False
    cfg = sys_config.Config()
    dirname = os.path.dirname(os.path.abspath(__file__))
    try:
        work_path = os.path.join(
            dirname+"/"+cfg.work_dir,
            str(solution_id))
        os.mkdir(work_path)
    except OSError as e:
        if str(e).find("exist") <= 0:  # 文件夹已经存在
            logger.error(e)
            return False
    try:
        real_path = os.path.join(
            dirname+"/"+cfg.work_dir,
            str(solution_id),
            file_name[pro_lang])
    except KeyError as e:
        logger.error(e)
        return False
    try:
        f = open(real_path, 'w')
        try:
            f.write(code)
            logger.info("solution_id({}) write code to file success".format(solution_id))
        except IOError as e:
            logger.error("%s can't write code to file" % solution_id)
            f.close()
            return False
        f.close()
    except OSError as e:
        logger.error("系统错误：", e)
        return False
    return True


if __name__ == '__main__':
    get_code(1, "gcc")
