#!/usr/bin/env python
# coding=utf-8

import logging

import protect
import judge_result
import judge_one


def judge(solution_id, problem_id, data_count, time_limit,
          mem_limit, program_info, result_des, language):
    """
    对题目进行评价
    :param solution_id:
    :param problem_id:
    :param data_count:
    :param time_limit:
    :param mem_limit:
    :param program_info:
    :param result_des:
    :param language:
    :return:
    """
    protect.low_level()
    max_mem = 0
    max_time = 0
    if language in ["java", 'python2', 'python3', 'ruby', 'perl']:
        time_limit = time_limit * 2
        mem_limit = mem_limit * 2
    for i in range(data_count):
        # 得到程序的运行时间,目前仍有错误
        # ret = judge_one.judge_one_mem_time(
        #     solution_id,
        #     problem_id,
        #     i + 1,
        #     time_limit + 10,
        #     mem_limit,
        #     language)
        # if ret is False:
        #     continue
        # if ret['result'] == result_des["Runtime Error"]:
        #     program_info['result'] = result_des["Runtime Error"]
        #     return program_info
        # elif ret['result'] == result_des["Time Limit Exceeded"]:
        #     program_info['result'] = result_des["Time Limit Exceeded"]
        #     program_info['take_time'] = time_limit + 10
        #     return program_info
        # elif ret['result'] == result_des["Memory Limit Exceeded"]:
        #     program_info['result'] = result_des["Memory Limit Exceeded"]
        #     program_info['take_memory'] = mem_limit
        #     return program_info
        # if max_time < ret["timeused"]:
        #     max_time = ret['timeused']
        # if max_mem < ret['memoryused']:
        #     max_mem = ret['memoryused']
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
