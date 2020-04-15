#!/usr/bin/env python
# -*- coding:utf-8 -*-

from compile import mysql_DBUtils


def update_problem_state(id_solution, state):
    mysql = mysql_DBUtils.MyPyMysqlPool()
    sql = "update solution set state = {1} where id_solution = {0}".format(id_solution, state)
    mysql.update(sql)
    mysql.dispose()


def get_problem_limit(id_problem):
    mysql = mysql_DBUtils.MyPyMysqlPool()
    sql = "select time_limit,mem_limit from problem where id_problem = {} limit 1".format(id_problem)
    ret = mysql.get_one(sql)
    mysql.dispose()
    return ret["time_limit"], ret["mem_limit"]


def get_result_des():
    mysql = mysql_DBUtils.MyPyMysqlPool()
    sql = "select name_result,id_result_des from result_des"
    ret = mysql.get_all(sql)
    mysql.dispose()
    result_des = {}
    for val in ret:
        result_des[val["name_result"]] = val["id_result_des"]
    return result_des

def write_compile_result(solution_id,reuslt):
    mysql = mysql_DBUtils.MyPyMysqlPool()
    sql = "update solution set compile_result = '{1}' where id_solution = {0}".format(solution_id, reuslt)
    mysql.update(sql)
    mysql.dispose()
    






