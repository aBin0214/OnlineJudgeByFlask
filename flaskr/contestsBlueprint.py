#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)

from . import MysqlUtils

bp = Blueprint('contests', __name__, url_prefix='/contests')

@bp.route("/contestSet")
def contestSet():
    g.active = "Contests"
    return render_template("contests/contestSet.html")