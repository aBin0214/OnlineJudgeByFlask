# -*- coding:utf-8 -*-

import subprocess
import os
import sys_config
import logging


def execute_compile(solution_id, language):
    """
        对称需进行编译
        :param solution_id:
        :param language:
        :return:
        """
    language = language.lower()
    cfg = sys_config.Config()
    dir_work = os.path.join(cfg.work_dir, str(solution_id))
    build_cmd = {
        "gcc": "gcc main.c -o main -Wall -lm -O2 -std=c99 --static -DONLINE_JUDGE",
        "g++": "g++ main.cpp -O2 -Wall -lm --static -DONLINE_JUDGE -o main",
        "java": "javac Main.java",
        "ruby": "reek main.rb",
        "perl": "perl -c main.pl",
        "pascal": 'fpc main.pas -O2 -Co -Ct -Ci',
        "go": '/opt/golang/bin/go build -ldflags "-s -w"  main.go',
        "lua": 'luac -o main main.lua',
        "python2": 'python2 -m py_compile main.py',
        "python3": 'python3 -m py_compile main.py',
        "haskell": "ghc -o main main.hs",
    }
    logger = logging.getLogger("sys_logger")
    if language not in build_cmd.keys():
        logger.info("solution_id:{} wrong language".format(solution_id))
        return False
    p = subprocess.Popen(
        build_cmd[language],
        shell=True,
        cwd=dir_work,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    out, err = p.communicate()  # 获取编译错误信息
    write_error(dir_work, out, err)
    if p.returncode == 0:  # 返回值为0,编译成功
        print("编译成功")
        logger.info("solution_id:{} compile success".format(solution_id))
        return True
    print("编译失败")
    logger.info("solution_id:{} compile failure".format(solution_id))
    return False


def write_error(dir_work, out, err):
    err_txt_path = os.path.join(dir_work, 'error.txt')
    f = open(err_txt_path, 'wb')
    f.write(err)
    f.write(out)
    f.close()


if __name__ == '__main__':
    execute_compile(1, "gcc")

