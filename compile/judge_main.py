#!/usr/bin/env python
# coding=utf-8

import logging

from compile import protect
from compile import judge_result
from compile import judge_one


def judge(solution_id, problem_id, data_count, time_limit,
          mem_limit, program_info, result_des, language):
    """
    对题目进行评价
    """
    protect.low_level()
    max_mem = 0
    max_time = 0
    if language in ["java", 'python2', 'python3', 'ruby', 'perl']:
        time_limit = time_limit * 2
        mem_limit = mem_limit * 2
    for i in range(data_count):
        # 得到程序的运行时间,目前尚未实现

        # 判断程序的运行结果是否正确
        result = judge_result.judge_result(problem_id, solution_id, i + 1)
        logger = logging.getLogger("sys_logger")
        logger.info(result)
        if result is False:
            continue
        if result == "Wrong Answer" or result == "Output limit":
            program_info['result'] = result_des[result]
            break
        elif result == 'Presentation Error':
            program_info['result'] = result_des[result]
        elif result == 'Accepted':
            if program_info['result'] != 'Presentation Error':
                program_info['result'] = result_des[result]
        else:
            logger = logging.getLogger("sys_logger")
            logger.error("judge did not get result")
    if program_info['result'] == 0:
        program_info['result'] = result_des['Wrong Answer']
    program_info['take_time'] = max_time
    program_info['take_memory'] = max_mem
    return program_info
