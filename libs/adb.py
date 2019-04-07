# -*- coding: utf-8 -*-
# !/usr/bin/env python

import random
import subprocess
import common
import execute
import platform

sys_plat = platform.system()  # 获取当前系统平台

throttle = "300"  # 事件间隔
pct_touch = "50"  # 触摸事件的百分比
pct_motion = "13"  # 动作事件的百分比
pct_trackball = "1"  # 轨迹事件的百分比
pct_syskeys = "1"  # 系统按键的百分比
pct_appswitch = "30"  # 启动Activity的百分比
pct_anyevent = "5"  # 其他类型事件的百分比


class ADB:
    def __init__(self, serial_number, package_name, run_time):
        self.serial_number = serial_number
        self.package_name = package_name
        self.run_time = run_time

    def monkey_go(self):
        seed = str(random.randint(0, 10000))  # 种子数
        print "种子数:", seed
        event_number = int(float(self.run_time) * 60 * 60 * 1000 / int(throttle))
        cmd = "adb -s %s shell monkey -p %s  --bugreport --ignore-crashes --ignore-timeouts --ignore-security-exceptions --monitor-native-crashes --kill-process-after-error -s %s --pct-trackball %s --pct-anyevent %s --pct-syskeys %s  --pct-appswitch  %s --pct-motion %s --pct-touch %s --throttle %s -v -v %s" % (
            self.serial_number, self.package_name, seed, pct_trackball, pct_anyevent, pct_syskeys, pct_appswitch, pct_motion,
            pct_touch, throttle, event_number)
        execute.excute_shell(cmd)

    def uninstall(self):
        cmd = "adb -s " + self.serial_number + " uninstall " + self.package_name
        execute.Command(cmd).run()

    def install(self, apk_name):
        cmd = "adb -s " + self.serial_number + " install -r -g " + apk_name
        execute.Command(cmd).run(timeout=120)

    def reboot(self):
        cmd = "adb -s " + self.serial_number + " reboot"
        execute.Command(cmd).run()

    def reconnect(self):
        if self.serial_number.__contains__(":"):
            cmd = "adb connect " + self.serial_number
            execute.Command(cmd).run()

    def disconnect(self):
        if self.serial_number.__contains__(":"):
            cmd =  "adb disconnect " + self.serial_number
            execute.Command(cmd).run()

    def delete_anr(self):
        cmd = "adb -s " + self.serial_number + " shell rm -rf sdcard/anr*"
        execute.Command(cmd).run()

    def get_adb_logcat(self,log_file):
        """
        get recently 10000 adb logcat.
        :return:
        """
        cmd = "adb -s " + self.serial_number + " logcat -t 10000 >" + log_file
        execute.Command(cmd).run()

    def stop_music(self):
        cmd = "adb -s " + self.serial_number + " shell input keyevent 86"
        execute.Command(cmd).run()

    def is_monkey_run(self):
        is_running = False
        cmd = "adb -s {serial_numer} shell ps | grep monkey".format(serial_numer=self.serial_number)
        # 兼容安卓高版本添加-A参数
        if common.get_device_version(self.serial_number) >= "6":
            cmd = "adb -s {serial_numer} shell ps -A | grep monkey".format(serial_numer=self.serial_number)

        if sys_plat == "Windows":
            cmd = "adb -s {serial_numer} shell ps | findstr monkey".format(serial_numer=self.serial_number)
            if common.get_device_version(self.serial_number) >= "6":
                cmd = "adb -s {serial_numer} shell ps -A | findstr monkey".format(serial_numer=self.serial_number)

        process = subprocess.Popen(cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   )
        stdout_list = process.communicate()[0].split('\n')
        print "判断是否有正在执行的monkey"
        for process in stdout_list:
            if process.__contains__("com.android.commands.monkey"):
                is_running = True
                print "monkey正在运行"
        return is_running


if __name__ == '__main__':
    pass

