#!/usr/bin/env python
# -*- coding:utf-8 -*-
import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash

from . import MysqlUtils
# from . import FormUtils


bp = Blueprint('base', __name__, url_prefix='/base')


@bp.route('/flashShow', methods=('GET', 'POST'))
def flashShow():
    return render_template("base/flash.html")