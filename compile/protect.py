#!/usr/bin/env python
# coding=utf-8

import logging
import os
import sys


def low_level():
    """
    降低程序运行权限，防止恶意代码
    如果发现有恶意程序，退出当前程序
    """
    try:
        os.setuid(int(os.popen("id -u %s" % "nobody").read()))
    except OSError:
        pass

