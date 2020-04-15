#!/usr/bin/env python
# -*- coding:utf-8 -*-

from queue import Queue
import threading
import time
import os
import sys
import logging

from compile import init_logger
from compile import protect
from compile import sys_config
from compile import producer
from compile import worker


def start_work_thread(cfg,queue,dbLock):
    """
    开启工作线程
    """
    for i in range(cfg.queue_size):  # 需要修改
        t = threading.Thread(target=worker.worker, name="worker", args=(queue, dbLock,))
        # t.deamon = True
        t.start()


def start_get_task(queue,dbLock):
    """
    开启获取任务线程
    """
    t = threading.Thread(target=producer.put_task_into_queue, name="get_task", args=(queue, dbLock,))
    t.deamon = True # 设置为守护进程
    t.start()


def check_thread():
    """
    检测评测程序是否存在,小于config规定数目则启动新的
    """
    cfg = sys_config.Config()
    protect.low_level()
    while True:
        try:
            if threading.active_count() < cfg.count_thread + 2:
                logger = logging.getLogger("sys_logger")
                logger.info("start new thread")
                t = threading.Thread(target=worker.worker)
                # t.deamon = True
                t.start()
            time.sleep(1)
        except:
            pass


def start_protect():
    """
    开启守护进程
    """
    protect.low_level()
    t = threading.Thread(target=check_thread, name="check_thread")
    # t.deamon = True
    t.start()


def judger_start():
    """
    整个程序的主函数
    """
    cfg = sys_config.Config()
    queue = Queue(cfg.queue_size)
    # 创建数据库锁，保证一个时间只能一个程序都写数据库
    dbLock = threading.Lock()
    init_logger.init_logger("sys_logger")  # 初始化log
    logger = logging.getLogger("sys_logger")
    logger.info("judge server is start")

    start_get_task(queue,dbLock)
    start_work_thread(cfg,queue,dbLock)
    start_protect()

if __name__ == "__main__":
    judger_start()