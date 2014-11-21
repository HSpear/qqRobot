#-*- coding:utf8 -*-

import os
import sys
import requests
import re
import json
import random
import time
import string
import logging
LOG_FORMAT='%(asctime)s %(filename)s[%(lineno)d] %(levelname)-8s> %(message)s'
logging.basicConfig(level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt='%m-%d %H:%M:%S',
)

import utils

CHECK_VERIFY_CODE_URL = "https://ssl.ptlogin2.qq.com/check"\
    "?uin={qq}&appid=1003903&js_ver=10062&js_type=0&r=0.6569391019121522"
CAPTCHA_URL = "http://captcha.qq.com/getimage"\
    "?aid=1003903&r=0.2509327069195215&uin={qq}"
LOGIN_URL = "https://ssl.ptlogin2.qq.com/login"\
    "?u={qq}&p={password}&verifycode={verifyCode}&webqq_type=10&remember_uin=1&login2qq=1"\
    "&aid=1003903&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html"\
    "%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052"\
    "&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=3-15-72115"\
    "&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10062&login_sig"\
    "=qBpuWCs9dlR9awKKmzdRhV8TZ8MfupdXF6zyHmnGUaEzun0bobwOhMh6m7FQjvWA"

HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Connection': 'keep-alive',
    'Content-Type': 'utf-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125'
                  'Safari/537.36',
}
REFERER_HEADER = {
    'Referer': 'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2',
}
MSG_FONT = {
    'name': '微软雅黑',
    'size': '10',
    'style': [0, 0, 0],
    'color': '000000'
}

class QQ(object):
    ''' Base class for QQ '''
    def __init__(self, qq, password):
        self.qq = qq
        self.password = password
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.clientid = None
        self.psessionid = None
        self.vfwebqq = None
        self.ptwebqq = None

        self.grouplist = {}

    def login(self):
        ''' QQ login '''
        status, verifyCode, encryptParams = self._checkIfNeedVerifyCode()
        # print status,type(status)
        if status != "0":
            self._getVerifyCodeImage()
            logging.info("请输入验证码...")
            verifyCode = raw_input()
        verifyCode = verifyCode.upper()
        status, _, url = self._loginStep1(verifyCode, encryptParams)
        self._loginStep2(url)
        self._loginStep3()

    def _checkIfNeedVerifyCode(self):
        ''' 检查是否需要验证码登录 '''
        r = self.session.get(CHECK_VERIFY_CODE_URL.format(qq=self.qq))
        #res.content would be like:
        #ptui_checkVC('1','DeVE9kBe36XN-e4J7TuAtNY3OSbX7b4n',\
        # '\x00\x00\x00\x00\x79\x50\x8e\x56', '');
        p = r"ptui_checkVC\('(\d)','(.*?)','(.*?)',.*"
        m = re.search(p, r.content)
        return m.groups()

    def _loginStep1(self, verifyCode, encryptParams):
        ''' step 1: 验证QQ,密码,验证码 '''
        password = utils.encryptPassword(self.password, verifyCode, encryptParams)
        # 该请求中的password是输入的password与验证码共同通过md5加密得到.
        r = self.session.get(LOGIN_URL.format(qq=self.qq,
                password=password, verifyCode=verifyCode))
        p = r"ptuiCB\('(\d)','(\d)','(.*?)',.*"
        m = re.search(p, r.content)
        return m.groups()

    def _loginStep2(self, url):
        ''' step 2: 打开step 1返回的url,获取cookie '''
        self.session.get(url)
        self.ptwebqq = self.session.cookies["ptwebqq"]

    def _loginStep3(self):
        ''' step 3: 打开channel页,获取vfwebqq psessionid '''
        url = "http://d.web2.qq.com/channel/login2"
        self.clientid = random.randint(10000000, 99999999) # 8位随机数
        data = {
            # "clientid": self.clientid,
            # "psessionid": "",
            "r": json.dumps({
                "status": "online",
                "passwd_sig": "",
                "clientid": self.clientid,
                "ptwebqq": self.ptwebqq,
                "psessionid": "",
            }),
        }
        _cookies = self.session.cookies
        self.session = requests.Session()  # 使用原来的session登录会有错误
        self.session.cookies.update(_cookies)
        res = self.session.post(url, data=data, headers=REFERER_HEADER)
        c = json.loads(res.content)
        if c['retcode'] == 0:
            self.vfwebqq = c['result']['vfwebqq']
            self.psessionid = c['result']['psessionid']
            logging.info("QQ登录成功...")
            return 0
        return 1

    def _getVerifyCodeImage(self):
        ''' 读取验证码图片, Mac '''
        # 图片url的参数已经存于self.session中
        return utils.showImageViaURL(CAPTCHA_URL.format(qq=self.qq), self.session)

    def _genHashCode(self):
        '''
        生成获取群信息所需要的hash code,
        参考:
            https://github.com/Shu-Ji/qqrobot
        WebQQ的hash code生成实现参考：
            http://0.web.qstatic.com/webqqpic/pubapps/0/50/eqq.all.js
        '''
        sQQ = str(self.qq)
        _a = self.ptwebqq + 'password error'
        _s = ''
        _j = []
        while 1:
            if len(_s) <= len(_a):
                _s += sQQ
                if len(_s) == len(_a):
                    break
            else:
                _s = _s[:len(_a)]
                break
        for d in range(len(_s)):
            _j.append(ord(_s[d]) ^ ord(_a[d]))

        _a = list(string.digits) + ['A', 'B', 'C', 'D', 'E', 'F']
        ret = ''
        for d in _j:
            ret += _a[d >> 4 & 15]
            ret += _a[d & 15]
        return ret

    def getGroupList(self):
        ''' 获取群信息 '''
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        if isinstance(self.vfwebqq, unicode):
            self.vfwebqq = self.vfwebqq.encode("utf8")
        data = {
            'r': json.dumps(
                {
                    'vfwebqq': self.vfwebqq,
                    'hash': self._genHashCode(),
                }),
        }
        #不加referer会返回100101，没有hash会返回50
        r = self.session.post(url, data=data, headers=REFERER_HEADER)
        content = json.loads(r.content)
        logging.info("group info: %s", r.content)
        if content['retcode'] == 0:
            result = content['result']
            for i in result['gnamelist']:
                self.grouplist[i['code']] = i
            logging.info("加载群信息成功...")
            logging.info(self.grouplist)
        else:
            logging.info("加载群信息失败! 错误码: %s", content['retcode'])

if __name__ == "__main__":
    logging.info("QQ 机器人开始启动...")
    qq = QQ(3067487368,"qqdianpingoa")
    qq.login()
    qq.getGroupList()
