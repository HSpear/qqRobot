#-*- coding:utf8 -*-

import urllib
import urllib2
import socket


def _hex2str(s):
    import binascii
    return binascii.a2b_hex(s)

def encryptPassword(pwd, token, params):
    from md5 import md5 as _md5
    md5 = lambda x: _md5(x).hexdigest().upper()
    pwd = _md5(pwd).hexdigest()
    params = params.replace("\\x", "")
    return md5(md5(_hex2str(pwd) + _hex2str(params)) + token.upper())

def showImageViaURL(url, browser=None):
    import StringIO
    import requests
    from PIL import Image
    if browser:
        r = browser.get(url)
    else:
        r = requests.get(url)
    img = Image.open(StringIO.StringIO(r.content))
    img.show()
    return 0

def urlGet(url):
    try:
        req = urllib2.Request(url)
        r = urllib2.urlopen(req)
        return r.read()
    except:
        print "Error : Connection refused for url : %s !" % url

def urlPost(url, data):
    try:
        req = urllib2.Request(url, urllib.urlencode(data))
        r = urllib2.urlopen(req)
        return r.read()
    except:
        print "Error : Connection refused for url : %s !" % url

def strEqual(s1, s2):
    if isinstance(s1, unicode):
        s1 = s1.encode('utf8')
    if isinstance(s2, unicode):
        s2 = s2.encode('utf8')
    return s1 == s2

def toUnicode(s):
    if isinstance(s, unicode):
        return s
    return s.decode('utf8')

def toStr(s):
    if isinstance(s, unicode):
        return s.encode('utf8')
    return s

def getLocalIp():
    # localIpAddr = socket.gethostbyname(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("www.baidu.com",80))
    localIpAddr = s.getsockname()[0]
    s.close()
    return localIpAddr

def testEncryptPassword():
    p = 'chris'
    t = 'kwPNZFUdF1HLcswe589_DrcCfr1juWO2'
    i = '\\x00\\x00\\x00\\x00\\x79\\x50\\x8e\\x56'
    print encryptPassword(p, t, i)


if __name__ == '__main__':
    testEncryptPassword()
