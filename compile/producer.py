#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time

import mysql_DBUtils
import get_code
import problem_util
import logging


def put_task_into_queue(que, db_lock):
    """
    循环扫描数据库,将任务添加到队列
    """
    while True:
        que.join()  # 阻塞程序,直到队列里面的任务全部完成
        sql = "select id_solution,id_problem,name_language\
                            from solution,pro_language \
                            where solution.id_language = pro_language.id_language \
                            and state = 12;"
        mysql = mysql_DBUtils.MyPyMysqlPool()
        data = mysql.get_all(sql)
        if data is False:
            continue
        time.sleep(0.2)  # 延时0.2秒,防止因速度太快不能获取代码
        for item in data:
            id_solution, id_problem, name_language = item["id_solution"], item["id_problem"], item["name_language"]
            db_lock.acquire()
            ret = get_code.get_code(id_solution, id_problem, name_language)
            db_lock.release()
            if ret is False:
                # 防止因速度太快不能获取代码
                time.sleep(0.5)
                db_lock.acquire()
                ret = get_code.get_code(id_solution, id_problem, name_language)
                db_lock.release()
            # # if ret is False:
            # #     db_lock.acquire()
            # #     # update_solution_state(solution_id, 11)
            # #     db_lock.release()
            # #     # clean_work_dir(solution_id)
            # #     continue
            task = {
                "solution_id": id_solution,
                "problem_id": id_problem,
                "pro_lang": name_language,
            }
            que.put(task)
            db_lock.acquire()
            problem_util.update_problem_state(id_solution, 8)  # 更新当前题目的状态为等待
            db_lock.release()
        time.sleep(0.5)

