# -*- coding: utf-8 -*-
# !/usr/bin/env python

import datetime
import time
import os
import glob
import subprocess
from optparse import OptionParser
import zipfile
import execute


def log(msg, stamp=True):
    """
    print timestamp and log
    :param msg: log 信息
    :param stamp: boolean
    :return:
    """
    try:
        if stamp:
            print get_time(), msg
        else:
            print msg
    except Exception as ex:
        print msg


def get_current_time():
    """
    get current time
    :return:
    """
    return datetime.datetime.now()


def get_current_seconds():
    """
    get current senconds
    :return:
    """
    return int(time.time())


def get_file_name_no_extension(path):
    """
    get the filename no extension,eg:./111/test.txt,return test
    :param path:String of path
    :return:String
    """
    return os.path.splitext(os.path.split(path)[1])[0]


def get_file_extension(path):
    """
    get file extension,eg:./111/test.txt,return .txt
    :param path:String of path
    :return:String
    """
    return os.path.splitext(os.path.split(path)[1])[1]


def get_file_name(path):
    """
    get the filename of the path.eg:./111/test.txt,return test.txt
    :param path: String of path
    :return:String
    """
    return os.path.split(path)[1]


def get_time():
    x = time.localtime()  # localtime参数为float类型，这里1317091800.0为float类型
    return time.strftime('%Y%m%d%H%M%S', x)


def get_apk_name():
    """
    get apk name
    :return: eg. test.apk
    """
    flist = glob.glob('*.apk')
    if len(flist) == 0:
        return ''
    return flist[-1]


def get_apk_name1():
    """
    get apk name
    :return: eg. test.apk
    """
    flist = glob.glob('*.yaml')
    if len(flist) == 0:
        return ''
    return flist[-1]

# =============================================
# cmd utils
# =============================================


def get_option_sns():
    all_SNS = get_sn()

    # get -s input devices data
    cmdLineParser = create_options()
    (options, args) = cmdLineParser.parse_args()
    devicesList = options.target

    if devicesList == None:
        appointDevices = all_SNS
    else:
        # Format devices data
        appointDevices = devicesList.split(',')
        all_SNS.sort(cmp=None, key=None, reverse=False)
        appointDevices.sort(cmp=None, key=None, reverse=False)

    print "matched Device list :"
    validDevices = [val for val in appointDevices if val in all_SNS]
    print validDevices

    print "not Found Devices :"
    print list(set(appointDevices).difference(set(all_SNS)))

    print "Free devices List :"
    print list(set(all_SNS).difference(set(appointDevices)))

    return validDevices


def create_options():
    """
    creates and returns a command line option parser
    """
    parser = OptionParser()

    parser.add_option("-s", "--target", action="store", type="string",
            dest="target", help="device id of target android phone, obtained with adb devices")

    return parser


def get_sn():
    '''
    '''
    result = run_cmd('adb devices')
    if not result[0]:
        return []
    relist = []
    for i in result[2].split('\n'):
        if 'List of devices attached' in i:
            continue
        if '\tdevice' in i and str(i).find('?') == -1:
            relist.append(str(i).split('\tdevice')[0])
    return relist


def run_cmd(cmd, mrp=None):
    '''
    '''
    stderrstring = ''
    stdoutstring = ''
    print "cmd:" + cmd
    p = subprocess.Popen(cmd, shell=True,  universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if mrp:
        while p.poll()==None or p.stdout.readline():
            tmp = p.stdout.readline()
            stdoutstring += tmp
            mrp.MonitorMonkeyResult(tmp)
            p.stdout.flush()
    else:
        stdoutstring, stderrstring = p.communicate()
    print stderrstring
    print stdoutstring
    if p.returncode == 0:
        return True, cmd, stdoutstring
    else:
        return False, cmd, stderrstring if stderrstring else stdoutstring


# =============================================
# file utils
# =============================================


def walk_root(root_dir, pre_file_name):
    """
    遍历目录,获取file_name前缀为pre_file_name 的文件列表
    :param root_dir:
    :param pre_file_name:文件名以什么开始
    :return:list
    """
    file_list = []
    list_dirs = os.walk(root_dir)
    for root, dirs, files in list_dirs:
        # for d in dirs:
        #     print os.path.join(root, d)
        for f in files:
            file_path = os.path.join(root, f)
            # print os.path.join(root, f)
            if os.path.split(file_path)[1].startswith(pre_file_name):
                file_list.append(file_path)
    return file_list


def zip(file_path):
    """
    zip file retrun zip_file_path
    :param file_path:String of file_path
    :return:
    """
    zip_file_path = os.path.splitext(file_path)[0] + ".zip"  # 压缩文件的名称
    f = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    f.write(file_path)
    return zip_file_path


def un_zip(file_name):
    """unzip zip file"""
    file_list = os.listdir(r'.')
    for file_name in file_list:
        if os.path.splitext(file_name)[1] == '.zip':
            print file_name
            file_zip = zipfile.ZipFile(file_name, 'r')
            for file in file_zip.namelist():
                file_zip.extract(file, r'.')
            file_zip.close()
            os.remove(file_name)


def write_to_lines(contents, file_path):
    """
    向文件内写入内容，可以写入数组，也可以写入字符串
    :param contents:
    :param file_path:
    :return:
    """
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, "w") as f:
        if isinstance(contents,tuple) or isinstance(contents,list):
            f.writelines(contents)
        else:
            f.write(contents)


def get_device_version(serial_number):
    """
    获得设备android版本
    :param serial_number:
    :return:
    """
    get_sys = ''.join(['adb -s ', serial_number, " shell getprop ro.build.version.release"])
    device_version = execute.get_result_of_shell(get_sys)
    return device_version


if __name__ == '__main__':
    print get_apk_name()
