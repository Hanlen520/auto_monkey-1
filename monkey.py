# coding=utf-8
# !/usr/bin/env python
# =============================================
# @File  : monkey.py
# @Author: XufeiLi
# @Date  : 2019/1/30
# @Desc  : monkey自动化入口
# =============================================
import sys
import monkey_config
import monkey_run

if __name__ == '__main__':
    if len(sys.argv) > 0:
        pkg_name = sys.argv[1]
        run_time = sys.argv[2]

        #  修改自动化配置
        monkey_config.PACKAGE_NAME = pkg_name.strip()
        monkey_config.RUN_TIME = run_time.strip()

        print "monkey time：" + run_time + "exe package：" + pkg_name

        print "monkey start !"
        monkey_run.run()
        print "monkey finished !"

    else:
        print "调用monkey,参数不合法"
        exit(1)
