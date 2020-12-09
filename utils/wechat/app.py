# -*- coding:utf-8 -*-
import base64
import json
import logging
import os
import sys

import requests
from Crypto.Cipher import AES
from urllib.parse import urlencode

from utils import generate_unique

logger = logging.getLogger(__name__)


class WXAppAuth(object):

    def __init__(self, app=None):
        self.auth_url = None
        self.app_id = None
        self.app_secret = None
        self.redis = None
        if app:
            self.init_app(app)
        self.app = app
        self.code_url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit'
        self.access_url = 'https://api.weixin.qq.com/cgi-bin/token'
        self.user_url = 'https://api.weixin.qq.com/cgi-bin/user/info'

    def init_app(self, app=None, redis=None):
        self.app = app
        self.auth_url = app.config.get('WX_AUTH_URL')
        self.app_id = app.config.get('WX_APP_ID')
        self.app_secret = app.config.get('WX_APP_SECRET')
        self.redis = redis
        if not self.auth_url:
            logger.error('没有配置WX_AUTH_URL')
            sys.exit(3)
        if not self.app_id:
            logger.error("没有配置WX_APP_ID")
            sys.exit(3)
        if not self.app_secret:
            logger.error("没有配置WX_APP_SECRET")
            sys.exit(3)

    def get_open_id(self, code):
        params = dict(
            appid=self.app_id,
            secret=self.app_secret,
            js_code=code,
            grant_type='authorization_code'
        )
        res = requests.get(self.auth_url, params=params)
        # print(res)
        data = res.json()
        logger.error(data)
        openid = data.get('openid')
        # user_info = requests.get(self.user_url,params={'openid':openid,'access_token':self.access_token})
        # logger.error(user_info.json())
        if data.get('openid'):
            logger.info("授权成功")
            return data
        else:
            logger.error("授权失败")
            return False

    @property
    def access_token(self):
        params = {'grant_type': 'client_credential',
                  'appid': self.app_id,
                  'secret': self.app_secret}
        access_token = self.redis.get('access_token')
        if not access_token:
            res = requests.get(self.access_url, params=params)
            data = res.json()
            # print(data)
            if data.get('access_token'):
                access_token = data.get('access_token')
                self.redis.set('access_token', access_token, expired=7000)
                logger.info("access_token缓存成功")
            else:
                logger.info("获取access_token失败")
                raise ValueError
        return access_token

    def get_code(self, scene=None, page=None):
        url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}'.format(self.access_token)
        param = {
            # "access_token": self.access_token,
            "scene": "test=1",
            "width": 240
        }
        if page:
            param['page'] = page
        if scene:
            param['scene'] = scene
        print(param)
        res = requests.post(url=url, json=param)
        # print(res.content)
        static_dir = self.app.config['STATIC_DIR']
        file_name = generate_unique(10) + '.png'
        path = os.path.join(static_dir, file_name)
        with open(path, 'wb') as f:
            f.write(res.content)
        return file_name
        # print(res.content)

    def check_message(self, message):
        url = 'https://api.weixin.qq.com/wxa/msg_sec_check'
        params = {'access_token': self.access_token}
        data = '{"content":"%s"}' % (message)
        res = requests.post(url, params=params, data=data.encode(), headers={'Content-Type': 'application/json'})
        data = res.json()
        if data.get('errcode') == 0:
            return None, False
        else:
            logger.info("不过审的言论")
            return data.get('errmsg'), True

    def get_phone(self, data):
        sessionKey = base64.b64decode(data.get('session_key'))
        encryptedData = base64.b64decode(data.get('phone_secret'))
        iv = base64.b64decode(data.get('iv'))

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))

        if decrypted['watermark']['appid'] != self.app_id:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s) - 1:])]
