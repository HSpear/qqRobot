#-*- coding:utf8 -*-

import os
import sys
import logging
LOG_FORMAT='%(asctime)s %(filename)s[%(lineno)d] %(levelname)-8s> %(message)s'
logging.basicConfig(level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt='%m-%d %H:%M:%S',
)

import simplejson as json
from bottle import Bottle, run, request, response, get, post

from lib.qqRobot import QQ
#from lib import utils


app = Bottle()
qqRobot = None

def startListen():
    run(app, host="0.0.0.0", port=8001)

@app.get("/robotInfo")
def robotInfo():
    data = {
        "qq": qqRobot.qq.qq,
        "qqName": qqRobot.qq.qqName,
        "status": qqRobot.qq.qqStatus,
        "groupList": qqRobot.qq.groupList,
    }
    return json.dumps({"status": 0, "data": data})

@app.post("/robotCommand")
def robotCommand():
    data = request.forms
    cmd = data.get("cmd", None)
    if cmd and hasattr(qqRobot, cmd):
        executer = getattr(qqRobot, cmd)
        #ret = executer(data)
        ret = executer()
    else:
        logging.error("Command[%s] not found...", cmd)
        ret = -1, "Command[%s] not found..." % cmd
    response.content_type = "application/json"
    if isinstance(ret, int):
        r = {"status": ret}
    elif isinstance(ret, (str, list, dict)):
        # str, list或dict，则返回的是数据
        r = {"status": 0, "data": ret}
    elif isinstance(ret, tuple):
        # tuple表示错误码和提示信息
        r = {"status": ret[0], "errorInfo": ret[1]}
    else:
        r = {"status": -2, "errorInfo": "Unknown error..."}
    return json.dumps(r)

class QQRobot(object):
    def __init__(self, qq, password):
        self.qq = QQ(qq, password)
        pass

    def getGroupList(self):
        data = self.qq.getGroupList()
        return data

if __name__ == "__main__":
    logging.info("QQ 机器人开始启动...")
    global qqRobot
    qqRobot = QQRobot(3040493963,"password")
    #th = Thread(target=startListen, args=[])
    #th.setDaemon(True)
    #th.start()
    run(app, host="0.0.0.0", port=8001)
