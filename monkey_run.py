# -*- coding: utf-8 -*-
# !/usr/bin/env python
# =============================================
# @File  : monkey_run.py
# @Author: XufeiLi
# @Date  : 2019/1/25
# @Desc  : monkey自动化启动
# =============================================
import os
import time
import multiprocessing
import monkey_config
from libs import common
from libs import execute
from libs.adb import ADB
from libs.execute import Command
import sys

start_time = common.get_current_seconds()
# 设定系统编码格式
reload(sys)
sys.setdefaultencoding('utf8')


def run():
    _init()  # 初始化操作
    devices_list = common.get_option_sns()  # 获取所有有效连接的设备序列号集合
    _multi_process(devices_list, monkey_config.PACKAGE_NAME, monkey_config.RUN_TIME)  # 现有设备多进程执行monkey
    _destory()


def _multi_process(devices, package_name, run_time):
    print "start multi process"
    jobs = []
    for serial_number in devices:
        p = multiprocessing.Process(target=_run_monkey, args=(serial_number, package_name, run_time))
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()


def _run_monkey(serial_number, package_name, run_time):
    adb = ADB(serial_number, package_name, run_time)
    apk_name = common.get_apk_name()  # 获取项目下apk全名
    if apk_name != "":
        print "use new apk"
        adb.uninstall()  # 卸载原有安装包
        adb.install(apk_name)  # 安装apk,默认时间
    else:
        print "use devices apk"
    # 开始执行monkey
    adb.monkey_go()
    # 监控monkey过程
    _monitor_log(adb)


def _monitor_log(adb):
    run_time = float(monkey_config.RUN_TIME) * 60 * 60  # 计算出monkey运行时间：秒
    while float(common.get_current_seconds() - start_time) < run_time:
        # TODO:monkey过程监控
        """
            do something
        """
        # 判断如果手机上不再有执行的monkey,重新启动monkey
        if not adb.is_monkey_run():
            print "restart monkey"
            adb.monkey_go()


def _init():
    # 停止所有设备monkey
    print "stop all monkey"
    execute.excute_shell("python monkey_stop.py -a")
    time.sleep(10)


def _destory():
    # 停止所有设备monkey
    print "stop all monkey"
    execute.excute_shell("python monkey_stop.py -a")
    time.sleep(60)


if __name__ == '__main__':
    run()

