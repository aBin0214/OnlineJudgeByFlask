#!/usr/bin/env python
# coding=utf-8

import os
import shlex
import logging
from ctypes import cdll

from compile import protect
from compile import sys_config
from compile import judge_box


def judge_result_mem_time(
        solution_id, problem_id, data_num, time_limit, mem_limit, language):
    """
    评测一组数据
    """
    protect.low_level()
    logger = logging.getLogger("sys_logger")
    cfg = sys_config.Config()
    dirname = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(
        dirname+"/"+cfg.data_dir, str(problem_id),
        'data_{}.in'.format(data_num))
    input_data = None
    output_path = os.path.join(
        dirname+"/"+cfg.work_dir, str(solution_id),
        'out_{}.txt'.format(data_num))
    if language == 'java':
        main_exe = 'java -cp %s Main' % (
            os.path.join(dirname+"/"+cfg.work_dir,
                         str(solution_id)))
    elif language == 'python2':
        main_exe = 'python2 %s' % (
            os.path.join(dirname+"/"+cfg.work_dir,
                         str(solution_id),
                         'main.pyc'))
    elif language == 'python3':
        main_exe = 'python3 %s' % (
            os.path.join(dirname+"/"+cfg.work_dir,
                         str(solution_id),
                         '__pycache__/main.cpython-33.pyc'))
    else:
        main_exe = os.path.join(dirname+"/"+cfg.work_dir, str(solution_id), 'main')
    res = judge_box.run(max_cpu_time=time_limit*1024,
                max_real_time=time_limit*1024,
                max_memory=mem_limit * 1024,
                max_process_number=200,
                max_output_size=10000,
                max_stack=32 * 1024 * 1024,
                exe_path=main_exe,
                input_path=input_path,
                output_path=output_path,
                error_path=output_path,
                args=[],
                env=[],
                log_path="judger.log",
                seccomp_rule_name="c_cpp",
                uid=0,
                gid=0)
    print(res)
    return res


if __name__ == '__main__':
    judge_result_mem_time(1, 1, 2, 1000, 65535, "gcc")
