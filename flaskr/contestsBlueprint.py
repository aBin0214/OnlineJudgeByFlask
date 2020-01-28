#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from . import MysqlUtils

bp = Blueprint('contests', __name__, url_prefix='/contests')

@bp.route("/contestSet")
@bp.route("/contestSet/<currentPage>")
def contestSet(currentPage=1):
    g.active = "Contests"
    session['currentPage_con'] = currentPage
    if session.get("contextId_con") is None:
        session["contextId_con"] = 1
    if session.get("pageSize") is None:
        session['pageSize'] = 20
    return render_template("contests/contestSet.html")