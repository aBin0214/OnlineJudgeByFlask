#!/usr/bin/env python
# coding=utf-8

import logging

import threading

from compile import protect
from compile import problem_util
from compile import problem_util
from compile import check_dangerous_code
from compile import compile_program
from compile import judge_main


def run(problem_id, solution_id, language, data_count, db_lock):
    """
    运行程序
    :param problem_id:
    :param solution_id:
    :param language:
    :param data_count:
    :param db_lock:
    :return:
    """
    protect.low_level()
    db_lock.acquire()
    time_limit, mem_limit = problem_util.get_problem_limit(problem_id)  # 获取程序执行时间和内存
    db_lock.release()
    program_info = {
        "solution_id": solution_id,
        "problem_id": problem_id,
        "take_time": 0,
        "take_memory": 0,
        "result": 0,
    }
    result_des = problem_util.get_result_des()
    if check_dangerous_code.check_dangerous_code(solution_id, language) is False:
        program_info['result'] = result_des["Runtime Error"]
        return program_info
    compile_result = compile_program.execute_compile(solution_id, language)
    if compile_result is False:  # 编译错误
        program_info['result'] = result_des["Compile Error"]
        return program_info
    if data_count == 0:  # 没有测试数据
        program_info['result'] = result_des["System Error"]
        return program_info
    result = judge_main.judge(
        solution_id,
        problem_id,
        data_count,
        time_limit,
        mem_limit,
        program_info,
        result_des,
        language)
    logger = logging.getLogger("sys_logger")
    logger.info(result)
    return result


if __name__ == '__main__':
    run(1, 1, "gcc", 3, threading.Lock())
