#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('proDetail', __name__, url_prefix='/proDetail')

from . import MysqlUtils

@bp.route("/problemDetail/<proNo>", methods=('GET', 'POST'))
def problemDetail(proNo):
    g.active = 'Problems'
    languages = getLanguages()
    if request.method == 'POST':
        if session.get('id_user') is None:
            flash('You need to log in first!')
            return render_template("proDetail/oneProblem.html",languages = languages)
        id_user = session.get('id_user');
        inputCode = request.form["inputCode"]
        if inputCode is None or inputCode == '':
            flash('Your answer is empty!')
            return render_template("proDetail/oneProblem.html",languages = languages)
        selectLanguage = request.form["selectLanguage"]
        id_language = -1;
        error = None
        for language in languages:
            if language['monaco_editor_val'] == selectLanguage:
                id_language = language["id_language"]
                break;
        if id_language != -1:
            print(id_user,inputCode,id_language)
            try:
                db = MysqlUtils.MyPyMysqlPool()
                sql = 'INSERT INTO solution (id_user,id_context_problem,id_language,submit_content) VALUES (\'{}\',\'{}\',\'{}\',\'{}\')'\
                    .format(id_user, proNo,id_language,inputCode)
                db.insert(sql)
            except:
                error = "user:{},problemNo:{}. submit answer failure".format(session.get("username"),proNo)
                current_app.logger.error(error)
            finally:
                db.dispose()
    return render_template("proDetail/oneProblem.html",languages = languages)

def getLanguages():
    db = MysqlUtils.MyPyMysqlPool()
    sql = "SELECT id_language,name_language,monaco_editor_val FROM pro_language;"
    languages = None
    try:
        languages = db.get_all(sql)
    except:
        current_app.logger.info("get languages failure !")
    finally:
        db.dispose()
    return languages

def getProblemInfo():
    pass