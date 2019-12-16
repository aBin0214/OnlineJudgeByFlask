#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import threading

import deal_data
import run_problem
import problem_util


def worker(que, db_lock):
    """
    工作线程，循环扫描队列，获得评判任务并执行
    :param db_lock:
    :param que:
    :return:
    """
    while True:
        logger = logging.getLogger("sys_logger")
        if que.empty() is True:  # 队列为空，空闲
            logger.info("%s idle" % threading.current_thread().name)
        task = que.get()  # 获取任务，如果队列为空则阻塞
        solution_id = task['solution_id']
        problem_id = task['problem_id']
        language = task['pro_lang']
        data_count = deal_data.get_data_count(task['problem_id'])  # 获取测试数据的个数
        logger.info("judging %s" % solution_id)
        result = run_problem.run(
            problem_id,
            solution_id,
            language,
            data_count,
            db_lock)  # 评判
        logger.info("%s result %s" % (result['solution_id'], result['result']))
        db_lock.acquire()
        logger.info(result["solution_id"]+result["result"])
        problem_util.update_problem_state(result["solution_id"], result["result"])  # 将结果写入数据库
        db_lock.release()
        # if config.auto_clean:  # 清理work目录
        #     clean_work_dir(result['solution_id'])
        que.task_done()  # 一个任务完成
