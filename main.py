#-*- coding:utf8 -*-

import os
import sys
import logging
LOG_FORMAT='%(asctime)s %(filename)s[%(lineno)d] %(levelname)-8s> %(message)s'
logging.basicConfig(level=logging.DEBUG,
    format=LOG_FORMAT,
    datefmt='%m-%d %H:%M:%S',
)


from lib.qqRobot import QQ
from lib import utils


if __name__ == "__main__":
    logging.info("QQ 机器人开始启动...")
    qq = QQ(3067487368,"qqdianpingoa")        
    qq.login()
    qq.getGroupList()
