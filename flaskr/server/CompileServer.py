#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flaskr.utils import MysqlUtils

def getCompileInfo(db):
    sql = "SELECT name_language,version,cmd FROM pro_language;"
    compileInfo = None
    try:
        compileInfo = db.get_all(sql)
    except:
        current_app.logger.info("get compile information failure !")
    if compileInfo is None or compileInfo is False:
        return []
    return compileInfo

def getResultDes(db):
    sql = "SELECT name_result,description FROM result_des;"
    resultsDes = None
    try:
        resultsDes = db.get_all(sql)
    except:
        current_app.logger.info("get result description failure !")
    if resultsDes is None or resultsDes is False:
        return []
    return resultsDes

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