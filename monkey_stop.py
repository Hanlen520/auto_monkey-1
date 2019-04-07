# -*- coding: utf-8 -*-
# !/usr/bin/env python
# =============================================
# @File  : monkey_stop.py
# @Author: XufeiLi
# @Date  : 2019/1/25
# @Desc  : monkey自动化停止
# =============================================
import getopt
import os
import sys
from libs import execute
from libs import common
import platform
sys_plat = platform.system()  # 获取当前系统平台


def _get_devices():
    os.system("adb start-server")

    device_list = execute.get_result_of_shell("adb devices").split("\n")
    # 1st line
    LIST_OF_DEVICES_ATTACHED = "List of devices attached"

    device_information_list = []

    for device in device_list:

        # Not the 1st line or the last line
        if device.find(LIST_OF_DEVICES_ATTACHED) == -1 and device.strip() != "":

            # device string example:"emulator-5554    device", "emulator-5554" is what we need
            serial_number = device.split()[0]
            device_information = _get_device_info(serial_number)

            # Update device status
            device_status = device.split()[1]
            device_information[KEY_DEVICE_STATUS] = device_status

            device_information_list.append(device_information)

    return device_information_list


def _print_devices():
    device_information_list = _get_devices()
    for device in device_information_list:
        info_connector = "__"
        print "".join([device[KEY_MANUFACTURER], info_connector,
                       device[KEY_BRAND], info_connector,
                       device[KEY_MODEL], info_connector,
                       device[KEY_VERSION], "\t\t",
                       device[KEY_DEVICE_STATUS], "\t",
                       device[KEY_SERIAL_NUMBER]])


KEY_SERIAL_NUMBER = 'ro.serialno'
KEY_DEVICE_STATUS = "status"  # unused

KEY_MANUFACTURER = 'ro.product.manufacturer'
KEY_BRAND = 'ro.product.brand'
KEY_MODEL = 'ro.product.model'
KEY_VERSION = 'ro.build.version.release'
KEY_DEVICE_NAME = 'deviceName'

"""
    Get device information.
    Device name example: samsung_samsung_GT-N7100_4.1.2

    Sample:
    table = get_device_info('4df12e0873de6f4b0')
    print table[KEY_SERIAL_NUMBER]
    print table[KEY_MANUFACTURER]
    print table[KEY_BRAND]
    print table[KEY_MODEL]
    print table[KEY_VERSION]
    print table[KEY_DEVICE_NAME]
"""


def _get_device_info(serial_number):

    command_basic_list = ["adb -s ", serial_number, " shell getprop "]
    command_basic = ''.join(command_basic_list)

    # These commands can get phone information
    command_manufacturer = command_basic + KEY_MANUFACTURER
    command_brand = command_basic + KEY_BRAND
    command_model = command_basic + KEY_MODEL
    command_version = command_basic + KEY_VERSION

    # Run commands and get output
    output_manufacturer = ''.join(execute.get_result_of_shell(command_manufacturer))
    output_brand = ''.join(execute.get_result_of_shell(command_brand))
    output_model = ''.join(execute.get_result_of_shell(command_model))
    output_version = ''.join(execute.get_result_of_shell(command_version))
    device_name = output_brand + '_' + output_model + '_' + output_version + '_' + serial_number

    # When device not found
    DEVICE_NOT_FOUND = "error: device not found"
    if(output_model == DEVICE_NOT_FOUND):
        print "Device " + serial_number + " not found."
        sys.exit()

    # Put information into a table
    table = {KEY_SERIAL_NUMBER:str(serial_number).strip(),
             KEY_MANUFACTURER:str(output_manufacturer).strip(),
             KEY_BRAND:output_brand, KEY_MODEL:output_model,
             KEY_VERSION:str(output_version).strip(),
             KEY_DEVICE_NAME:str(device_name).strip(),
             KEY_DEVICE_STATUS:"device"}
    return table

# import commands
PACKAGE_MONKEY = "com.android.commands.monkey"


def _help_message():
    print ("Kill Monkey\n"
           "  -a --all\t\tkill monkey on all devices\n"
           "  -s <specific device>\tkill monkey on a device with the given serial number\n")


def _get_pid(serial_number):
    command_list_processes = ''.join(['adb -s ', serial_number, " shell ps | grep ", PACKAGE_MONKEY])
    # 兼容安卓高版本添加-A参数
    get_sys = ''.join(['adb -s ', serial_number, " shell getprop ro.build.version.release"])
    phone_sys = execute.get_result_of_shell(get_sys)
    if common.get_device_version(serial_number) >= "6":
        command_list_processes = ''.join(['adb -s ', serial_number, " shell ps -A | grep ", PACKAGE_MONKEY])
    process_list = execute.get_result_of_shell(command_list_processes).split("\n")
    for line in process_list:
        if line.find(PACKAGE_MONKEY) != -1:
            # line may be like this:
            # USER     PID   PPID  VSIZE  RSS     WCHAN    PC         NAME
            # root     5567  862   187736 19988   ffffffff 400422d8 S com.android.commands.monkey
            process_monkey_info_list = line.split()
            return process_monkey_info_list[1]
    # If monkey process doesn't exist.
    return None


def _kill_by_pid(serial_number, pid):
    command_kill = ''.join(["adb -s ", serial_number, " shell kill -9 ", pid])
    process_kill = os.system(command_kill)


def _kill(serial_number):
    pid = _get_pid(serial_number)
    if pid != None:
        _kill_by_pid(serial_number, pid)


def _kill_monkey(serial_number):
    _kill(serial_number)


def stop_monkey():
    devices_information_list = _get_devices()
    list_length = len(devices_information_list)

    # No any device
    if list_length == 0:
        print "No device found"
        sys.exit()

    if len(sys.argv) < 2:
        # No arguments
        if list_length == 1:
            # Kill monkey on the only one device
            print "kill " + devices_information_list[0][KEY_SERIAL_NUMBER]
            _kill_monkey(devices_information_list[0][KEY_SERIAL_NUMBER])
            print "Monkey killed on ", devices_information_list[0][KEY_DEVICE_NAME]
        else:
            _print_devices()
            _help_message()
    else:
        # With arguments
        try:
            opts, args = getopt.getopt(sys.argv[1:], "has:", ["help", "all"])

            # Show help message when command is like this:"python kill.py eeee".
            # The 1st argument doesn't contain a "-".
            if len(opts) == 0 :
                _help_message()
                sys.exit()

            for op, value in opts:
                if op in ("-h", "--help"):
                    # Help
                    _help_message()
                    sys.exit()
                elif op in ("-s"):
                    # A specific device
                    serial_number = value
                    _kill_monkey(serial_number)
                    sys.exit()
                elif op in ("-a", "--all"):
                    # All devices
                    for device in devices_information_list:
                        _kill_monkey(device[KEY_SERIAL_NUMBER])
                        print "Monkey killed on ", device[KEY_DEVICE_NAME]
                    sys.exit()
                else:
                    # Other arguments
                    _help_message()
                    sys.exit()
        except getopt.GetoptError:
            # Deal with wrong args
            _help_message()
            sys.exit()


if __name__ == '__main__':
    stop_monkey()
