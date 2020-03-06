#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.utils import MysqlUtils

bp = Blueprint('base', __name__, url_prefix='/base')

@bp.route('/showFlash', methods=('GET', 'POST'))
def showFlash():
    return render_template("base/flash.html")

@bp.route("/loading",methods=("GET","POST"))
def loading():
    return render_template("base/loading.html")