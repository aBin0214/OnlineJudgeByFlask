#!/usr/bin/env python
# coding=utf-8

import logging
import os

from compile import protect
from compile import sys_config

def judge_result(problem_id, solution_id, data_num):
    """
    对输出数据进行评测
    """
    protect.low_level()
    logger = logging.getLogger("sys_logger")
    config = sys_config.Config()
    logger.debug("solution {},data {},Judging result".format(solution_id, data_num))
    dirname = os.path.dirname(os.path.abspath(__file__))
    correct_result = os.path.join(
        dirname+"/"+config.data_dir, str(problem_id), 'data_%s.out' %
        data_num)
    user_result = os.path.join(
        dirname+"/"+config.work_dir, str(solution_id), 'out_%s.txt' %
        data_num)
    try:
        correct = open(correct_result).read().replace('\r', '').rstrip()  # 删除\r,删除行末的空格和换行
        user = open(user_result).read().replace('\r', '').rstrip()
        print(correct,user)
    except IOError as e:
        return False
    if correct == user:  # 完全相同:AC
        return "Accepted"
    if correct.split() == user.split():  # 除去空格,tab,换行相同:PE
        return "Presentation Error"
    if correct in user:  # 输出多了
        return "Output limit"
    return "Wrong Answer"  # 其他WA

if __name__ == "__main__":
    judge_result(1,61,1)

