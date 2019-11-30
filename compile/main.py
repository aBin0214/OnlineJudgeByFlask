#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import init_logger
import protect


def main():
    protect.low_level()  # 降低程序运行条件
    init_logger.init_logger("sys_logger")
    logger = logging.getLogger("sys_logger")
    logger.info("判题系统已启动。")


if __name__ == '__main__':
    main()
