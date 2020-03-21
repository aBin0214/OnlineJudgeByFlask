#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import logging

from compile import mysql_DBUtils
from compile import get_code
from compile import problem_util



def put_task_into_queue(que, db_lock):
    """
    循环扫描数据库,将任务添加到队列
    """
    while True:
        que.join()  # 阻塞程序,直到队列里面的任务全部完成
        sql = "select id_solution,id_problem,s.id_contest_problem,name_language\
                from solution as s,pro_language as pl,contest_problem as cp \
                where s.id_language = pl.id_language \
                and  s.id_contest_problem = cp.id_contest_problem \
                and state = 12;"
        mysql = mysql_DBUtils.MyPyMysqlPool()
        db_lock.acquire()
        data = mysql.get_all(sql)
        db_lock.release()
        if data is False:
            continue
        time.sleep(0.2)  # 延时0.2秒,防止因速度太快不能获取代码
        for item in data:
            id_solution, id_problem, id_contest_problem, name_language = \
                item["id_solution"], item["id_problem"], item["id_contest_problem"], item["name_language"]
            db_lock.acquire()
            ret = get_code.get_code(id_solution, name_language)
            db_lock.release()
            if ret is False:
                # 防止因速度太快不能获取代码
                time.sleep(0.5)
                db_lock.acquire()
                ret = get_code.get_code(id_solution, name_language)
                db_lock.release()
            # if ret is False:
            #     db_lock.acquire()
            #     # update_solution_state(solution_id, 11)
            #     db_lock.release()
            #     # clean_work_dir(solution_id)
            #     continue
            task = {
                "solution_id": id_solution,
                "problem_id": id_problem,
                "contest_problem_id":id_contest_problem,
                "pro_lang": name_language,
            }
            que.put(task)
            db_lock.acquire()
            problem_util.update_problem_state(id_solution, 8)  # 更新当前题目的状态为等待
            db_lock.release()
        time.sleep(0.5)

