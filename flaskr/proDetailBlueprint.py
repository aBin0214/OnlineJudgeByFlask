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
    languages = getLanguages()
    if request.method == 'POST':
        selectLanguage = request.form["selectLanguage"]
        id_language = -1;
        for language in languages:
            if language['monaco_editor_val'] == selectLanguage:
                id_language = language["id_language"]
                break;
        if id_language != -1:
            pass
        
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