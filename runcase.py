#!/usr/bin/env python2.7
# -*- coding:UTF-8 -*-

import os
import re
import sys
import time
import random
import logging
import unittest
import threading
import writeconf
import subprocess
import traceback
import ConfigParser
import HTMLTestRunner
import multiprocessing
from time import sleep
from logModule import add_log
from appium import webdriver

reload(sys)
sys.setdefaultencoding('utf-8')
cf = ConfigParser.ConfigParser()
cf.read("drivers.conf")
number = 1

class MyTest(unittest.TestCase):

    def setUp(self):        
        """
        初始化信息
        """
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        add_log(self.udid, "===============================================")
        add_log(self.udid, "case start time is " + start_time)
        desired_caps={}
        desired_caps["platformName"] = "Android"
        desired_caps["platformVersion"] = "*"
        desired_caps["deviceName"] = "*"
        desired_caps['udid'] = self.udid
        desired_caps["automationName"] = "Appium"
        desired_caps["appPackage"] = "com.xueersi.monkeyabc.app"
        desired_caps["appActivity"] = "com.xueersi.yummy.app.business.splash.SplashActivity"
        desired_caps["noReset"] = "True"
        desired_caps["newCommandTimeout"] = "2400"
        add_log(self.udid, "http://127.0.0.1:{}/wd/hub || udid is {}".format(self.port, self.udid))  
        self.driver = webdriver.Remote("http://127.0.0.1:{}/wd/hub".format(self.port),desired_caps)
        #self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub",desired_caps)
        self.driver.implicitly_wait(5)

    @staticmethod
    def getTestFunc(lesson_id):
        def func(self):
            test(driver=self.driver, udid=self.udid, lesson_id=lesson_id)
        return func

    def tearDown(self):
        end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        add_log(self.udid, "case quite time is " + end_time) 
        add_log(self.udid, '===============================================')
        self.driver.quit()


def test(udid, lesson_id, driver):
    """
    @summary  自动化case单元
    @param lesson_id  课程表页课程id
    """
    try:
        driver.find_element_by_accessibility_id('学习').click()
        driver.find_element_by_id("com.xueersi.monkeyabc.app:id/menuRL").click()
        course_id = lesson_id % 5 + 1
        driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout'\
            '/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.'\
            'widget.RelativeLayout/android.view.ViewGroup/androidx.recyclerview.widget.RecyclerView/'\
            'android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.RelativeLayout[{}]'.\
            format(course_id)).click() 
        add_log(udid, "course_id is {}".format(course_id))
        session_list = [3, 5, 6, 7]
        session_id = random.choice(session_list)
        driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout'\
            '/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.'\
            'widget.RelativeLayout/androidx.recyclerview.widget.RecyclerView/android.widget.RelativeLayout[{}]'\
            .format(session_id)).click()
        add_log(udid, "session_id is {}".format(session_id))
        sleep(200)
    except Exception as e:
        traceback.format_exc()
        add_log(udid, traceback.format_exc())


def generateTestCases(section):
    """
    @summary 为类添加case
    @param section conf文件中的section
    """
    conf = read_conf(section)
    setattr(MyTest, 'udid', conf[0])
    setattr(MyTest, 'port', conf[1])
    for args in range(1,200):
        setattr(MyTest, 'test{}'.format(args), MyTest.getTestFunc(args))
        add_log(conf[0], "填入属性test{}".format(args))


def read_conf(section):
    udid = cf.get(section, "udid")
    port = cf.get(section, "port")
    bootstrap_port = cf.get(section, "bootstrap_port")
    selendroid_port = cf.get(section, "selendroid_port")
    return udid, port, bootstrap_port, selendroid_port


def kill_process(port):
    """
    @summary 调用adb命令kill端口对应的进程
    """
    #print() "lsof -n -i:{} | grep LISTEN | awk \'{{print $2}}\' | xargs kill".format(port)
    return_code = subprocess.call("lsof -n -i:{} | grep LISTEN | awk \'{{print $2}}\' | xargs kill".format(port), shell=True)
    if return_code != 0:
        print "kill process fail"
        return False 
    else:
        print "kill process success"
        return True


def start_appium(thread_name, section):
    conf = read_conf(section)
    port = conf[1] 
    bootstrap_port = conf[2]
    selendroid_port = conf[3]
    add_log(conf[0], conf)
    try:
        cmd = "node /Applications/Appium.app/Contents/Resources/app/node_modules"\
            "/appium/build/lib/main.js --port {} --bootstrap-port {} --selendroid-port {}"\
            .format(port, bootstrap_port, selendroid_port)
        add_log(conf[0], "cmd: " + cmd)
        return_code = subprocess.call(cmd, shell=True)
        add_log(conf[0], 'return_code:{}'.format(return_code)) 
        if return_code != 0:
            add_log(conf[0], "start appium cmd not exce, port is {}, thread is {}".format(port, thread_name))
            return False
        else:
            add_log(conf[0], "start appium, port is {}, thread is {}".format(port, thread_name))
            #event.set(True)
            return True
    except:
        add_log(conf[0], "start appium cmd not exce, port is {}, thread is {}".format(port, thread_name))
        return False


def run_case(thread_name, section):
    add_log(read_conf(section)[0], "automation star")
    #event.wait()
    add_log(read_conf(section)[0], "{} run case Thread is {} \n".format(section, thread_name))
    generateTestCases(section)
    unittest.main()
    add_log(read_conf(section)[0], "automation end")


def run_appium_process():
    sections = cf.sections()
    global number 
    threads = []
    for section in sections:
        #event = threading.Event()
        appium_thread = multiprocessing.Process(target=start_appium, args=("Process-{}".format(number), section, ))
        threads.append(appium_thread)
        number += 1

    for appium_thread in threads:
        appium_thread.start()
        time.sleep(10)
    # for thread in threads:
    #     thread.join()


def run_case_process():
    sections = cf.sections()
    global number 
    threads = []
    for section in sections:
        #event = threading.Event()
        case_thread = multiprocessing.Process(target=run_case, args=("Process-{}".format(number), section, ))
        case_thread.start()
        time.sleep(10)
        threads.append(case_thread)
        number += 1

    for case_thread in threads:
        case_thread.join()
# def run_appium_thread():
#     sections = cf.sections()
#     number = 1
#     threads = []
#     for section in sections:
#         #event = threading.Event()
#         appium_thread = threading.Thread(target=start_appium, args=("Thread-{}".format(number), section, ))
#         threads.append(appium_thread)
#         number += 1

#     for appium_thread in threads:
#         appium_thread.start()
#         time.sleep(10)
#     # for thread in threads:
#     #     thread.join()


# def run_case_thread():
#     sections = cf.sections()
#     number = 1
#     threads = []
#     for section in sections:
#         #event = threading.Event()
#         case_thread = threading.Thread(target=run_case, args=("Thread-{}".format(number), section, ))
#         case_thread.start()
#         time.sleep(10)
#         threads.append(case_thread)
#         number += 1

#     for case_thread in threads:
#         case_thread.join()


def kill_appium():
    sections = cf.sections()
    for section in sections:
        conf = read_conf(section)
        port = conf[1]
        kill_process(port)


if __name__ == '__main__':
    writeconf.get_devices()
    writeconf.WriteConf().write_conf()
    run_appium_process()
    run_case_process()
    kill_appium()
  


    



        
