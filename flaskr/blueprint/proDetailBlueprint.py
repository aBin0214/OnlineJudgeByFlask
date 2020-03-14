#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app,jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from pyecharts import options as opts
from pyecharts.charts import Pie
from jinja2 import Markup
from pyecharts.globals import ThemeType  

from flaskr.utils import MysqlUtils
from flaskr.utils import ProblemUtils

from flaskr.server import CompileServer
from flaskr.server import ProblemServer

bp = Blueprint('proDetail', __name__, url_prefix='/proDetail')

@bp.route("/problemDetail/<proNo>", methods=['GET'])
def problemDetail(proNo):
    db = MysqlUtils.MyPyMysqlPool()
    languages = CompileServer.getLanguages(db)
    problemInfo = ProblemServer.getProblemInfo(db,proNo)
    problemInfo["describe"] = ProblemUtils.readProblemDescribe(problemInfo["id_problem"])["content"]
    problemTags = ProblemServer.getProblemTags(db,proNo)
    g.proNo = proNo
    db.dispose()
    return render_template("proDetail/oneProblem.html",languages = languages,problemInfo=problemInfo,problemTags=problemTags)

@bp.route("/submitCode",methods=['POST'])
def submitCode():
    db = MysqlUtils.MyPyMysqlPool()

    error = None
    if session.get('id_user') is None:
        error = 'You need to log in first!'
    if error is None:
        id_user = session.get('id_user');
        inputCode = request.form.get("inputCode")
        if inputCode is None or inputCode == '':
            error = 'Your answer is empty!'
    if error is None:
        selectLanguage = request.form.get("selectLanguage")
        id_language = -1;
        languages = CompileServer.getLanguages(db)
        for language in languages:
            if language['monaco_editor_val'] == selectLanguage:
                id_language = language["id_language"]
                break;
        if id_language != -1:
            solution = {}
            solution["id_user"] = id_user
            solution["id_contest_problem"] = proNo
            solution["id_language"] = id_language
            solution["submit_content"] = inputCode
            if ProblemServer.insertSolution(db,solution):
                flash('Answer submitted successfully!','success')
                db.dispose()
                return jsonify({
                    "result":"success"
                })
            else:
                error = "user:{},problemNo:{}. submit answer failure".format(session.get("username"),proNo)
    db.dispose()
    flash(error,"danger")
    return jsonify({
        "result":"failure",
        "error":error
    })

@bp.route("problemReport",methods=['POST'])
def problemReport():
    db = MysqlUtils.MyPyMysqlPool()
    proNo = request.form.get("id_problem")
    graphType = request.form.get("graphType")
    print(proNo,graphType)
    if graphType == "simple":
        graph = getSampleGraph(db,proNo)
    elif graphType == "statistics":
        graph = getStatisticsGraph(db,proNo)
    db.dispose()
    return Markup(graph.render_embed())

def getSampleGraph(db,proNo):
    proSubmissions = ProblemServer.getProSubmissions(db,proNo)
    acceptedCnt,WrongCnt = 0,0
    for sub in proSubmissions:
        if sub["id_result_des"] == 11:
            acceptedCnt = sub["cnt"]
        else:
            WrongCnt += sub["cnt"]
    pie = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT,width="180px", height="200px"))
        .add("", [list(z) for z in zip(["AC","WA"],[acceptedCnt,WrongCnt])])
        .set_colors(["#28a745", "red"]) 
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    )
    return pie

def getStatisticsGraph(db,proNo):
    proSubmissions = ProblemServer.getProSubmissions(db,proNo)
    nameList, valueList = [],[]
    for sub in proSubmissions:
        nameList.append(sub["name_result"])
        valueList.append(sub["cnt"])
    if proSubmissions == []:
        nameList.append("submission")
        valueList.append(0)
    pie = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT,width="480px", height="510px"))
        .add("", [list(z) for z in zip(nameList,valueList)])
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    )
    return pie

    