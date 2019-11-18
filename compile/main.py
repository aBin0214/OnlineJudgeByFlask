# -*- coding:utf-8 -*-

import logging
import init_logger


def start():
    init_logger.init_logger("sys_logger")
    logger = logging.getLogger("sys_logger")
    logger.info("判题系统已启动。")


if __name__ == '__main__':
    start()
