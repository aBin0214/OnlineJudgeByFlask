#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app,jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('proDetail', __name__, url_prefix='/proDetail')

from . import MysqlUtils

@bp.route("/problemDetail/<proNo>", methods=['GET'])
def problemDetail(proNo):
    db = MysqlUtils.MyPyMysqlPool()
    languages = getLanguages(db)
    problemInfo = getProblemInfo(db,proNo)
    g.proNo = proNo
    db.dispose()
    return render_template("proDetail/oneProblem.html",languages = languages,problemInfo=problemInfo)

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

def getLanguages(db):
    sql = "SELECT id_language,name_language,monaco_editor_val FROM pro_language;"
    languages = None
    try:
        languages = db.get_all(sql)
    except:
        current_app.logger.info("get languages failure !")
    return languages

def getProblemInfo(db,idContestProblem):
    sql = "SELECT cp.serial,cp.id_contest_problem,p.id_problem,title,create_by,time_limit,mem_limit \
        FROM problem as p,contest_problem as cp \
        where p.id_problem = cp.id_problem \
        and cp.id_contest_problem = {id_contest_problem} limit 1;".format(id_contest_problem=idContestProblem)
    problemInfo = None
    try:
        problemInfo = db.get_one(sql)
    except:
        current_app.logger.info("get problem information failure !")
    return problemInfo