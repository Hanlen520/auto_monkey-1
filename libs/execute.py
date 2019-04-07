# -*- coding: utf-8 -*-
# !/usr/bin/env python

import subprocess
import tempfile
import threading
import traceback
import time


def get_result_of_shell(run_cmd, time_out=5):
    """
    run the cmd
    :param time_out:
    :param run_cmd:
    :return:
    """
    from what import What
    w = What(*(run_cmd.split()))
    wait_time = time_out
    while wait_time >= 0:
        if w.get_output().__len__() == 0:
            time.sleep(1)
        else:
            return w.get_output()
        wait_time -= 1
    else:
        return ""


def excute_shell(cmd):
    print "_______________________________________________________"
    print cmd
    try:
        out_temp = tempfile.SpooledTemporaryFile(bufsize=10 * 1000)
        fileno = out_temp.fileno()
        obj = subprocess.Popen(cmd, stdout=fileno, stderr=fileno, shell=True)
        out_temp.seek(0)
    except Exception, e:
        print traceback.format_exc()
    finally:
        if out_temp:
            out_temp.close()
    return obj


def get_cmd_return_state(run_cmd):
    run_cmd = run_cmd.split(" ")
    popen = subprocess.Popen(run_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    run_result = popen.stdout.readlines()
    popen.wait()
    print popen.returncode
    return run_result


class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def target(self):
        self.process = subprocess.Popen(self.cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        run_result = self.process.stdout.readlines()
        self.process.wait()
        returncode = self.process.returncode
        print "_______________________________________________________"
        print self.cmd
        if returncode == 1:
            print str(False)
            print run_result
        else:
            print str(True)
            print run_result
        return returncode

    def target_no_output(self):
        self.process = subprocess.Popen(self.cmd, shell=True, universal_newlines=True, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        run_result = self.process.stdout.readlines()
        self.process.wait()
        returncode = self.process.returncode
        print "_______________________________________________________"
        print self.cmd
        if returncode == 1:
            print str(False)
        else:
            print str(True)
            print run_result
        return returncode

    def run(self, no_ouput=False, timeout=60):
        target = self.target
        if no_ouput:
            target = self.target_no_output
        try:
            thread = threading.Thread(target=target)
            thread.start()

            thread.join(timeout)
            if thread.is_alive():
                self.process.terminate()
                thread.join()
                return False
            return True
        except Exception as ex:
            print ex.message
            return False
