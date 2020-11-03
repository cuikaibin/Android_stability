#!/usr/bin/env python2.7
# -*- coding:UTF-8 -*-


import os
import time


def add_log(driver, msg):
    file = mkdir(driver)
    exec_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(file, 'a') as f:
        f.write("{} || {}\n".format(exec_time, msg))
    f.close()


def mkdir(driver):
    creat_time = time.strftime("%Y-%m-%d", time.localtime())
    pwd = os.getcwd()
    path = "{}/log/{}".format(pwd, creat_time)
    is_exists = os.path.exists(path)
    if not is_exists:
        os.makedirs(path)
    file = "{}/{}.log".format(path, driver)
    return file




        