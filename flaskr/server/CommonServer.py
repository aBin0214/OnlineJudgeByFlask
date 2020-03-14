#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import current_app
from flaskr.utils import MysqlUtils

def selectIdentity(db):
    sql = "select @@IDENTITY limit 1"
    res = None
    try:
        res = db.get_one(sql)
    except:
        current_app.logger.error("select identity failure.")
    if res is False or res is None:
        return -1
    return res['@@IDENTITY']