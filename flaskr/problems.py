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
        session["problemTheme"] = "ALL"
    if session.get("contextId") is None:
        session["contextId"] = 0
    if session.get("totalPages") is None:
        if session.get("contextId") == 0:
            session["totalPages"] = getCount(session.get("problemTheme"))
    
    return render_template("problems/problemSet.html")


def getProblemsByTheme(currentPage,problemTheme):
    db = MysqlUtils.MyPyMysqlPool()
    sql = ""
    pass

def getCount(problemTheme):
    db = MysqlUtils.MyPyMysqlPool()
    sql = "";
    if problemTheme == "All":
        sql = "select count('id_problem') as cnt from problem limit 1"
    else:
        sql = "select count('id_problem') as cnt \
        from online_judge.problem , online_judge.tag_problem, online_judge.tag \
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

def getProblemsByContext(context):
    pass

