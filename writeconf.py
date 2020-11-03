#!/usr/bin/env python2.7
# -*- coding:UTF-8 -*-

import socket
import subprocess
import ConfigParser
from logModule import add_log

class WriteConf(object):
    """
    @summary 读取连接电脑的手机数量并为其配置appium启动参数
    """
    def __init__(self):
        super(WriteConf, self).__init__()
        self.cf = ConfigParser.ConfigParser()
        self.driver_number = 0
        self.driver_port_list = [0, 4722, 8080]

    def write_conf(self):
        """
        @summmary 为每个生成driver配置appium启动参数:udid,port,bootstrap-port,selendroid-port
        """
        with open('devices', 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.rstrip()
                add_log(line, line) 
                self.driver_number += 1
                section = "device{}".format(self.driver_number)
                self.cf.add_section(section)
                self.port_list(list)
                self.cf.set(section, "udid", str(line))
                self.cf.set(section, "port", str(self.driver_port_list[0]))
                self.cf.set(section, "bootstrap_port", str(self.driver_port_list[1]))
                self.cf.set(section, "selendroid_port", str(self.driver_port_list[2]))
                with open("drivers.conf", "w+") as f:
                    self.cf.write(f)               

    def port_list(self, driver):
        """
        @summary 检验启动appium端口是否被占用，并写入list
        """
        self.driver_port_list[0] = self.driver_port_list[1] + 1
        while check_port(self.driver_port_list[0], driver) is False:
            self.driver_port_list[0] = self.driver_port_list[0] + 1

        self.driver_port_list[1] = self.driver_port_list[0] +  1
        while check_port(self.driver_port_list[1],driver) is False:
            self.driver_port_list[1] = self.driver_port_list[1] + 1

        self.driver_port_list[2]  += 1
        while check_port(self.driver_port_list[2], driver) is False:
            self.driver_port_list[2] += 1
        add_log(driver, "port list is {}".format(self.driver_port_list))


def get_devices():
    """
    @summary 调用adb命令写入连接电脑手机的uid
    """
    return_code = subprocess.call("adb devices | awk \'$2==\"device\"{print() $1}\' > devices", shell=True)
    if return_code != 0:
        print "get drivers list fail"
        return False 


def check_port(port, driver, host='0.0.0.0'):
    """
    @summary 检测端口是否被占用
    @param   port    检验的端口
    @param   host    默认参数，默认本机ip
    @return  Flase   端口被占用
    @return  True    端口可以正常使用
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, int(port)))
        s.shutdown(2)
        add_log(driver, "port {} is uesd !".format(port))
        return False
    except:
        add_log(driver, "port {} is available!".format(port))
        return True


if __name__ == '__main__':
    get_devices() 
    WriteConf().write_conf()












