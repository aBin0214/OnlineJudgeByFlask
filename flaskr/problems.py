#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from . import MysqlUtils

bp = Blueprint('problems', __name__, url_prefix='/problems')

@bp.route("/problemSet")
def problemSet():
    if session.get("currentPage") is None:
        session["currentPage"] = 1
    if session.get("problemTheme") is None:
        session["problemTheme"] = "All"
    if session.get("contextId") is None:
        session["contextId"] = 0
    if session.get("totalCount") is None:
        if session.get("contextId") == 0:
            session["totalCount"] = getCount(session.get("problemTheme"))
    currentPage = int(session.get("currentPage"))
    problemTheme = session.get("problemTheme")
    problems = getProblemsByTheme(currentPage,problemTheme)
    idx = 0
    for problem in problems:
        problemId = problem["id_problem"]
        problems[idx]["accepted_count"] = getAcceptedCount(problemId)
        problems[idx]["submit_count"] = getSubmitCount(problemId)
        idx += 1
    return render_template("problems/problemSet.html",problems=problems)


def getProblemsByTheme(currentPage,problemTheme):
    db = MysqlUtils.MyPyMysqlPool()
    sql = ""
    start = (currentPage-1)*20;
    end = min(currentPage*20-1,int(session.get("totalCount")))
    if problemTheme == "All":
        sql = "select id_problem,title from problem limit {start},{end};".format(start=start,end=end)
    else:
        sql = "select problem.id_problem,title \
        from online_judge.problem , online_judge.tag, online_judge.tag_problem \
        where problem.id_problem = tag_problem.id_problem \
        and tag.id_tag = tag_problem.id_tag \
        and tag.name_tag = '{theme}' limit {start},{end}".format(theme=problemTheme,start=start,end=end)
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
        sql = "select count(id_problem) as cnt from problem limit 1"
    else:
        sql = "select count(problem.id_problem) as cnt \
        from problem,tag_problem, tag \
        where problem.id_problem = tag_problem.id_problem \
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
    from online_judge.solution as s,online_judge.context_problem as c, \
    online_judge.result_des as r \
    where s.id_context_problem = c.id_context_problem \
    and s.state = r.id_result_des \
    and r.name_result = \"Accepted\" \
    and c.id_problem = {}".format(problemId);
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
    from online_judge.solution as s,online_judge.context_problem as c \
    where s.id_context_problem = c.id_context_problem \
    and c.id_problem = {}".format(problemId);
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.info("get problems accepted count failure !")
    finally:
        db.dispose()
    return res["cnt"]

def getProblemsByContext(context):
    pass

