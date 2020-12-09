from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from flask import Flask
import logging
import sys
import random
import json
from utils.api import abort

logger = logging.getLogger(__name__)


class Ali(object):

    def __init__(self, app=None, redis=None):
        self.app = app
        self.access_key_id = None
        self.access_secret = None
        self.client = None
        if isinstance(app, Flask):
            self.init_app(app, redis)

    def init_app(self, app, redis):
        self.app = app
        # 校验url是不是有效的
        self.access_key_id = app.config.get('ACCESS_KEY_ID')
        if not self.access_key_id:
            logger.error("ACCESS_KEY_ID未设置")
            sys.exit(3)
        self.access_secret = app.config.get('ACCESS_SECRET')
        if not self.access_secret:
            logger.error("ACCESS_SECRET未设置")
            sys.exit(3)
        self.client = AcsClient(self.access_key_id, self.access_secret, 'cn-hangzhou')
        self.redis = redis

    def send_message(self, phone):
        # 随机生成6位数字符串
        phone = str(phone)
        code = str(random.randint(100000, 999999))
        self.redis.set(phone, code, expired=300)
        req = CommonRequest()
        req.set_accept_format('json')
        req.set_domain('dysmsapi.aliyuncs.com')
        req.set_method('POST')
        req.set_protocol_type('https')  # https | http
        req.set_version('2017-05-25')
        req.set_action_name('SendSms')
        req.add_query_param('RegionId', "cn-hangzhou")
        req.add_query_param('PhoneNumbers', str(phone))
        req.add_query_param('SignName', "速用工")
        req.add_query_param('TemplateCode', "SMS_172380192")
        req.add_query_param('TemplateParam', "{\"code\":\"%s\"}" % (code))
        response = json.loads(self.client.do_action(req), encoding='utf-8')

        if response.get('Code') == "OK":
            return True
        else:
            logger.error(response)
            abort(400, message="操作频繁 稍后再试")
            return False

    def check(self, phone, code):
        code = str(code)
        r_code = self.redis.get(phone)
        if r_code == code:
            self.redis.delete(phone)
            return True
        else:
            return False
