#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from . import MysqlUtils

bp = Blueprint('problems', __name__, url_prefix='/problems')

@bp.route("/problemSet/<int:currentPage>")
@bp.route("/problemSet")
def problemSet(currentPage=1):
    g.active = "Problems"

    session['currentPage'] = currentPage
    # if session.get("currentPage") is None:
    #     session["currentPage"] = 1
    if session.get("problemTheme") is None:
        session["problemTheme"] = "All"
    if session.get("contestId") is None:
        session["contestId"] = 1
    if session.get("pageSize") is None:
        session['pageSize'] = 20
    session['pageSize'] = 20
    
    totalCount = getCount(session.get("problemTheme"))
    total = totalCount//session.get("pageSize")
    total = total if totalCount%session.get("pageSize") == 0 else total+1
    session['totalPage'] = total

    currentPage = int(session.get("currentPage"))
    problemTheme = session.get("problemTheme")
    problems = getProblemsByTheme(currentPage,problemTheme,session.get("pageSize"))

    print("当前页数：",currentPage)
    print("总页数：",session.get("totalPage"))
    idx = 0
    for problem in problems:
        problemId = problem["id_contest_problem"]
        problems[idx]["accepted_count"] = getAcceptedCount(problemId)
        problems[idx]["submit_count"] = getSubmitCount(problemId)
        idx += 1
    return render_template("problems/problemSet.html",problems=problems)


def getProblemsByTheme(currentPage,problemTheme,pageSize):
    db = MysqlUtils.MyPyMysqlPool()
    sql = ""
    start = (currentPage-1)*pageSize
    if problemTheme == "All":
        sql = "select id_contest_problem,title \
        from contest_problem,problem \
        where contest_problem.id_contest = '{id_contest}' \
        and contest_problem.id_problem = problem.id_problem\
        limit {start},{pageSize};".format(id_contest=1,start=start,pageSize=pageSize)
    else:
        sql = "select id_contest_problem,title \
        from problem,tag,tag_problem,contest_problem \
        where contest_problem.id_contest = '{id_contest}' \
        and contest_problem.id_problem = problem.id_problem \
        and problem.id_problem = tag_problem.id_problem \
        and tag.id_tag = tag_problem.id_tag \
        and tag.name_tag = '{theme}' limit {start},{pageSize}".format(id_contest=1,theme=problemTheme,start=start,pageSize=pageSize)
    problems = None
    try:
        problems = db.get_all(sql)
    except:
        current_app.logger.info("get problems failure !")
    finally:
        db.dispose()
    return problems

def getCount(problemTheme):
    db = MysqlUtils.MyPyMysqlPool()
    sql = "";
    if problemTheme == "All":
        sql = "select count(id_contest_problem) as cnt from online_judge.contest_problem where id_contest = '1'"
    else:
        sql = "select count(contest_problem.id_contest_problem) as cnt \
        from contest_problem,problem,tag_problem,tag \
        where contest_problem.id_contest = '1' \
        and contest_problem.id_problem = problem.id_problem \
        and problem.id_problem = tag_problem.id_problem \
        and tag.id_tag = tag_problem.id_tag \
        and tag.name_tag = '{}' limit 1".format(problemTheme);
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.info("get problems count failure !")
    finally:
        db.dispose()
    return res["cnt"]

def getAcceptedCount(problemId):
    db = MysqlUtils.MyPyMysqlPool()
    sql = "select count(id_solution) as cnt \
    from online_judge.solution as s,online_judge.result_des as r \
    where s.state = r.id_result_des \
    and r.name_result = \"Accepted\" \
    and s.id_contest_problem = {}".format(problemId);
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.info("get problems accepted count failure !")
    finally:
        db.dispose()
    return res["cnt"]

def getSubmitCount(problemId):
    db = MysqlUtils.MyPyMysqlPool()
    sql = "select count(id_solution) as cnt \
    from online_judge.solution as s \
    where s.id_contest_problem = {}".format(problemId);
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.info("get problems accepted count failure !")
    finally:
        db.dispose()
    return res["cnt"]

def getProblemsBycontest(contest):
    pass

