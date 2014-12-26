import os
import re
import time
import inspect
import logging
import requests
import multiprocessing
import logging.handlers

now_time = time.strftime("%Y%m%d%H")
print now_time

fmt_str = '[%(levelname).4s %(asctime)s.%(msecs)03d pid:%(process)d] %(message)s'
date_str = '%y-%m-%d %H:%M:%S'
handler = logging.handlers.RotatingFileHandler('discuz.%s.log' % now_time , maxBytes=10*1024*1024)

handler.setFormatter(logging.Formatter(fmt=fmt_str, datefmt=date_str))
discuzlog = logging.getLogger(__name__)
discuzlog.setLevel(logging.DEBUG)
discuzlog.propagate = False

discuzlog.addHandler(handler)

def parseText(resp):
    data = ''
    for chunk in resp.iter_content(8192):
        data += chunk
    return data

def _post(session, url, form):
    retry = 0
    while retry < 3:
        try:
            p = session.post(url, form, timeout=1)
        except requests.Timeout:
            discuzlog.warning("retry=%s url=%s form=%s" % (retry, url, form))
            retry += 1
            if retry == 3:
                raise(requests.Timeout)
        else:
            return p

def _get(session, url):
    retry = 0
    while retry < 3:
        try:
            p = session.get(url, timeout=1)
        except requests.Timeout:
            discuzlog.warning("retry=%s url=%s" % (retry, url))
            retry += 1
            if retry == 3:
                raise(requests.Timeout)
        else:
            return p

class Robot:
    def __init__(self, domain, username, passwd):
        self.name = 'Discuz Robot'
        self.domain = domain
        self.username = username
        self.passwd = passwd
        self.Login()

    def _job(self, session, url, form):
        discuzlog.debug('user=%s method=_job' % (self.username, ))
        p = _post(session, url, form)
        data = parseText(p)
        res = re.match('.*<div class="c">\r\n([^<]*).*', data, re.DOTALL)
        msg = res.group(1)
        discuzlog.info('stage=%s user=%s message=%s' % (self.stage, self.username, msg))

    def Login(self):
        self.stage = 'Login'
        self.session = requests.Session()
        url = self.domain + '/member.php?mod=logging&action=login'
        form = {'username': self.username, 'password': self.passwd, 'loginsubmit': 'true'}
        _post(self.session, url, form)

    def GetFormhash(self):
        self.stage = 'GetFormhash'
        retry = 0
        while retry < 3:
            try:
                p = self.session.get(self.domain + '/forum.php', timeout=1)
                data = parseText(p)
                res = re.match('.*name\=\"formhash\"\ value\=\"([^"]*)\".*', data, re.DOTALL)
                self.hashval = res.group(1)
            except Exception as e:
                retry = retry + 1
                discuzlog.warning('stage=%s user=%s retry=%s' % \
                        (self.stage, self.username, retry))
                if retry == 3:
                    with open(type(e).__name__, 'w+') as f:
                        f.write(data)
                    raise(e)
            else:
                break

    def multiPost(self, url, form):
        try:
            for i in range(5):
                pid = os.fork()
                if pid == 0:
                    self._job(self.session, url, form)
                    exit()
        except Exception as e:
            discuzlog.error('stage=%s user=%s exception=%s message=%r' % \
                    (self.stage, self.username, type(e).__name__, str(e)))
            exit()
        
    def multiGet(self, url):
        discuzlog.error('stage=%s user=%s exception=%s message=%r' % \
                (self.stage, self.username, '1', '1',))
        try:
            for i in range(5):
                pid = os.fork()
                if pid == 0:
                    _get(self.session, url)
                    exit()
        except Exception as e:
            discuzlog.error('stage=%s user=%s exception=%s message=%r' % \
                    (self.stage, self.username, type(e).__name__, str(e)))
            exit()

    def QianDao(self):
        self.GetFormhash()
        self.stage = 'QianDao'
        url = self.domain + '/plugin.php?id=dsu_paulsign:sign' \
                            '&operation=qiandao&infloat=1&inajax=1'
        form = {'qdxq': 'kx', 'qdmode': '2', 'formhash': self.hashval, 'fastreply': '0'}

        self.multiPost(url, form)

    def WeekTask(self):
        self.GetFormhash()
        self.stage = 'WeekTask'
        url = self.domain + 'home.php?mod=task&do=apply&id=68'

        self.multiGet(url)


Robot('http://bbs.zjut.edu.cn', 'mhb','8888891d3ea5ec27c39033b69120a18f').QianDao()
Robot('http://bbs.zjut.edu.cn', 'polym','8888891d3ea5ec27c39033b69120a18f').QianDao()
Robot('http://bbs.zjut.edu.cn', 'QNMLGB','8888891d3ea5ec27c39033b69120a18f').QianDao()
