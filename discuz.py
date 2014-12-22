import re
import logging
import logging.handlers
import requests

fmt_str = '[%(levelname)s %(asctime)s.%(msecs)03d pid:%(process)d] %(message)s'
date_str = '%y-%m-%d %H:%M:%S'
handler = logging.handlers.RotatingFileHandler('discuz.log', maxBytes=10*1024*1024, backupCount=5)

handler.setFormatter(logging.Formatter(fmt=fmt_str, datefmt=date_str))
discuzlog = logging.getLogger(__name__)
discuzlog.setLevel(logging.DEBUG)
discuzlog.addHandler(handler)

def parseText(resp):    
    data = ''
    for chunk in resp.iter_content(8192):
        data += chunk
    return data

class Robot:
    def __init__(self, domain, username, passwd):
        self.name = 'Discuz Robot'
        self.domain = domain
        self.username = username
        self.passwd = passwd
        self.cookie = ''

    def sign_in(self):
        try:
            session = requests.Session()
            url = self.domain + '/member.php?mod=logging&action=login'
            form = {'username': self.username, 'password': self.passwd, 'loginsubmit': 'true'}
            p = session.post(url, form, timeout=2)

            p = session.get(self.domain + '/forum.php', timeout=2)
            data = parseText(p)
            res = re.match('.*name\=\"formhash\"\ value\=\"([^"]*)\".*', data, re.DOTALL)
            hashval = res.group(1)
            
            url = self.domain + '/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&inajax=1'
            form = {'qdxq': 'kx', 'qdmode': '2', 'formhash': hashval, 'fastreply': '0'}
            p = session.post(url, form, timeout=2)
            data = parseText(p)
            res = re.match('.*<div class="c">\r\n([^<]*).*', data, re.DOTALL)
            msg = res.group(1)
            discuzlog.info('user: %s %s' % (self.username, msg))
        except Exception as e:
            discuzlog.error('user: %s %s %s' % (self.username, type(e).__name__, str(e)))


Robot('http://bbs.zjut.edu.cn', 'mhb','8888891d3ea5ec27c39033b69120a18f').sign_in()
Robot('http://bbs.zjut.edu.cn', 'polym','8888891d3ea5ec27c39033b69120a18f').sign_in()
Robot('http://bbs.zjut.edu.cn', 'QNMLGB','8888891d3ea5ec27c39033b69120a18f').sign_in()
