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
# 内置主题类型可查看 pyecharts.globals.ThemeType
from pyecharts.globals import ThemeType  

from flaskr.utils import MysqlUtils
from flaskr.utils import ProblemUtils

bp = Blueprint('proDetail', __name__, url_prefix='/proDetail')

@bp.route("/problemDetail/<proNo>", methods=['GET'])
def problemDetail(proNo):
    db = MysqlUtils.MyPyMysqlPool()
    languages = getLanguages(db)
    problemInfo = getProblemInfo(db,proNo)
    problemInfo["describe"] = ProblemUtils.readProblemDescribe(problemInfo["id_problem"])["content"]
    problemTags = getProblemTags(db,proNo)
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
        languages = getLanguages(db)
        for language in languages:
            if language['monaco_editor_val'] == selectLanguage:
                id_language = language["id_language"]
                break;
        if id_language != -1:
            try:
                proNo = request.form.get("proNo")
                sql = 'INSERT INTO solution (id_user,id_contest_problem,id_language,submit_content) VALUES (\'{}\',\'{}\',\'{}\',\'{}\')'\
                    .format(id_user, proNo,id_language,inputCode)
                print(sql)
                db.insert(sql)
                flash('Answer submitted successfully!','success')
                db.dispose()
                return jsonify({
                    "result":"success"
                })
            except:
                error = "user:{},problemNo:{}. submit answer failure".format(session.get("username"),proNo)
                current_app.logger.error(error)
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
    proSubmissions = getProSubmissions(db,proNo)
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
    proSubmissions = getProSubmissions(db,proNo)
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

def getLanguages(db):
    sql = "SELECT id_language,name_language,monaco_editor_val FROM pro_language;"
    languages = None
    try:
        languages = db.get_all(sql)
    except:
        current_app.logger.info("get languages failure !")
    if languages is None or languages is False:
        return []
    return languages

def getProblemInfo(db,idContestProblem):
    sql = "SELECT cp.serial,cp.id_contest,cp.id_contest_problem,p.id_problem,p.title as problemTitle,c.title as contestTitle,create_by,time_limit,mem_limit,username " \
        "FROM problem as p,contest_problem as cp,contest as c,user as u " \
        "where p.id_problem = cp.id_problem " \
        "and cp.id_contest = c.id_contest " \
        "and p.create_by = u.id_user " \
        "and cp.id_contest_problem = {id_contest_problem} limit 1;".format(id_contest_problem=idContestProblem)
    problemInfo = None
    try:
        problemInfo = db.get_one(sql)
    except:
        current_app.logger.info("get problem information failure !")
    if problemInfo is None or problemInfo is False:
        return {}
    return problemInfo

def getProblemTags(db,idContestProblem):
    sql = "select t.id_tag,name_tag " \
        "from tag as t ,tag_problem as tp ,contest_problem as cp " \
        "where tp.id_problem = cp.id_problem " \
        "and t.id_tag = tp.id_tag " \
        "and cp.id_contest_problem = {}".format(idContestProblem)
    problemTags = None
    try:
        problemTags = db.get_all(sql)
    except:
        current_app.logger.info("get problem tags failure !")
    if problemTags is None or problemTags is False:
        return []
    return problemTags

def getProSubmissions(db,idContestProblem):
    sql = "SELECT id_result_des,name_result,count(id_solution) as cnt "\
        "FROM online_judge.result_des as rd,online_judge.solution as s " \
        "where rd.id_result_des = s.state " \
        "and s.state not in (8,12) " \
        "and s.id_contest_problem = {} " \
        "group by rd.id_result_des".format(idContestProblem)
    proSubmissions = None
    try:
        proSubmissions= db.get_all(sql)
    except:
        current_app.logger.info("get problem submissions failure !")
    if proSubmissions is None or proSubmissions is False:
        return []
    return proSubmissions

    