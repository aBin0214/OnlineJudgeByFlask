#!/usr/bin/env python
# coding=utf-8

import os
import shlex
import logging
from ctypes import cdll

from compile import protect
from compile import sys_config


def judge_one_mem_time(
        solution_id, problem_id, data_num, time_limit, mem_limit, language):
    """
    评测一组数据
    """
    protect.low_level()
    logger = logging.getLogger("sys_logger")
    cfg = sys_config.Config()
    input_path = os.path.join(
        cfg.data_dir, str(problem_id),
        'data_{}.in'.format(data_num))
    input_data = None
    try:
        input_data = open(input_path, "r")
    except IOError as e:
        logger.critical("solution {},data_{}.in,read error{}"
                        .format(solution_id, data_num, e))
    dirname = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(
        dirname+"/"+cfg.work_dir, str(solution_id),
        'out_{}.txt'.format(data_num))
    temp_out_data = None
    try:
        temp_out_data = open(output_path, "w")
    except IOError as e:
        logger.critical("solution {},data_{}.out,read error{}"
                        .format(solution_id, data_num, e))
    if language == 'java':
        cmd = 'java -cp %s Main' % (
            os.path.join(dirname+"/"+cfg.work_dir,
                         str(solution_id)))
        main_exe = shlex.split(cmd)  # split 函数提供了和shell 处理命令行参数时一致的分隔方式
    elif language == 'python2':
        cmd = 'python2 %s' % (
            os.path.join(dirname+"/"+cfg.work_dir,
                         str(solution_id),
                         'main.pyc'))
        main_exe = shlex.split(cmd)
    elif language == 'python3':
        cmd = 'python3 %s' % (
            os.path.join(dirname+"/"+cfg.work_dir,
                         str(solution_id),
                         '__pycache__/main.cpython-33.pyc'))
        main_exe = shlex.split(cmd)
    elif language == 'lua':
        cmd = "lua %s" % (
            os.path.join(dirname+"/"+cfg.work_dir,
                         str(solution_id),
                         "main"))
        main_exe = shlex.split(cmd)
    elif language == "ruby":
        cmd = "ruby %s" % (
            os.path.join(dirname+"/"+cfg.work_dir,
                         str(solution_id),
                         "main.rb"))
        main_exe = shlex.split(cmd)
    elif language == "perl":
        cmd = "perl %s" % (
            os.path.join(dirname+"/"+cfg.work_dir,
                         str(solution_id),
                         "main.pl"))
        main_exe = shlex.split(cmd)
    else:
        main_exe = [os.path.join(dirname+"/"+cfg.work_dir, str(solution_id), 'main'), ]
    run_cfg = {
        'args': main_exe,
        'fd_in': input_data.fileno(),
        'fd_out': temp_out_data.fileno(),
        'timelimit': time_limit,  # in MS
        'memorylimit': mem_limit,  # in KB
    }
    protect.low_level()
    input_data.close()
    temp_out_data.close()


if __name__ == '__main__':
    judge_one_mem_time(1, 1, 2, 1000, 65535, "gcc")
