#-*- coding:utf8 -*-

import os
import sys
import logging
LOG_FORMAT='%(asctime)s %(filename)-20s[%(lineno)d] %(levelname)-8s> %(message)s'
logging.basicConfig(level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt='%m-%d %H:%M:%S',
)

import simplejson as json
from bottle import Bottle, run, request, response, get, post

from lib.qqRobot import QQ
from lib import utils


app = Bottle()
global qqRobot
qqRobot = None

def startListen(port):
    run(app, host="0.0.0.0", port=port)

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
        ret = executer(data)
    else:
        logging.error("Command[%s] not found...", cmd)
        ret = -1, "Command[%s] not found..." % cmd
    response.content_type = "application/json"
    if isinstance(ret, int):
        r = {"status": ret}
    elif isinstance(ret, (list, dict)):
        # list或dict，则返回的是数据
        r = {"status": 0, "data": ret}
    elif isinstance(ret, tuple):
        # tuple表示错误码和提示信息
        r = {"status": ret[0], "errorInfo": ret[1]}
    elif isinstance(ret, str):
        r = {"status": 1, "info": ret}
    else:
        r = {"status": -1, "error": "未知错误..."}
    return json.dumps(r)

# 这样不至于将QQ的所有接口暴露出来
class QQRobot(object):
    def __init__(self, qq, password):
        self.qq = QQ(qq, password)
        pass

    def getGroupList(self, data):
        return self.qq.getGroupList()

    def getGroupMembers(self, data):
        return self.qq.getGroupMembers(int(data['groupId']))

    def getGroupMsgs(self, data):
        return self.qq.getGroupMsgs(int(data['groupId']))

    def sendGroupMsg(self, data):
        return self.qq.sendGroupMsg(int(data['groupId']), utils.toStr(data['msg']))

    def sendFriendMsg(self, data):
        return self.qq.sendFriendMsg(int(data['friendId']), utils.toStr(data['msg']))

if __name__ == "__main__":
    logging.info("QQ 机器人开始启动...")
    #global qqRobot
    qqRobot = QQRobot(3040493963,"password")
    #qqRobot = QQRobot(3067487368,"qqdianpingoa")
    #th = Thread(target=startListen, args=[])
    #th.setDaemon(True)
    #th.start()
    startListen(8001)
