#!/usr/bin/env python
# coding=utf-8

"""
__init__.py有两个作用：
一是包含应用工厂；
二是告诉Python flaskr文件夹应视作一个包
"""

import os
import sys
from flask import Flask
from compile import *

def create_app(test_config=None):
    """
    创建并配置app
    :param test_config:
    :return:
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev"
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #backstage judger start
    judger_main.judger_start()

    from flaskr.utils import LoggerUtils
    LoggerUtils.init_logger()

    from flaskr.blueprint import authBlueprint
    app.register_blueprint(authBlueprint.bp)

    from flaskr.blueprint import homeBlueprint 
    app.register_blueprint(homeBlueprint.bp)
    app.add_url_rule('/', endpoint='index')

    from flaskr.blueprint import baseBlueprint
    app.register_blueprint(baseBlueprint.bp)

    from flaskr.blueprint import contestDetailBlueprint
    app.register_blueprint(contestDetailBlueprint.bp)

    from flaskr.blueprint import contestsBlueprint
    app.register_blueprint(contestsBlueprint.bp)

    from flaskr.blueprint import proDetailBlueprint
    app.register_blueprint(proDetailBlueprint.bp)

    from flaskr.blueprint import userBlueprint
    app.register_blueprint(userBlueprint.bp)

    from flaskr.blueprint import adminBlueprint
    app.register_blueprint(adminBlueprint.bp)

    return app
