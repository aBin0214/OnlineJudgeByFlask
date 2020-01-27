#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.authBlueprint import login_required
from . import MysqlUtils

bp = Blueprint('home', __name__)

@bp.route("/")
def index():
    g.active = "Home"
    compileInfo = getCompileInfo()
    resultsDes = getResultDes()
    return render_template("home/home.html",compileInfo=compileInfo,resultsDes=resultsDes)

def getCompileInfo():
    db = MysqlUtils.MyPyMysqlPool()
    sql = "SELECT name_language,version,cmd FROM pro_language;"
    compileInfo = None
    try:
        compileInfo = db.get_all(sql)
    except:
        current_app.logger.info("get compile information failure !")
    finally:
        db.dispose()
    return compileInfo

def getResultDes():
    db = MysqlUtils.MyPyMysqlPool()
    sql = "SELECT name_result,description FROM result_des;"
    resultsDes = None
    try:
        resultsDes = db.get_all(sql)
    except:
        current_app.logger.info("get result description failure !")
    finally:
        db.dispose()
    return resultsDes

