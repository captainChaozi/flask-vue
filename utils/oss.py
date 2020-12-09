import datetime
import logging
import random
import sys
import time

import oss2

logger = logging.getLogger()


class OssOP(object):

    def __init__(self, app=None,
                 access_key_id=None,
                 access_key_secret=None,
                 endpoint=None,
                 bucket_name=None,
                 oss_domain=None):
        self.app = app
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.oss_domain = oss_domain

    def init_app(self, app=None):
        self.app = app
        self.validate_config()

    def validate_config(self):
        config = ('OSS_KEY_ID', 'OSS_KEY_SECRET', 'OSS_BUCKET', 'OSS_ENDPOINT')
        for i in config:
            if i not in self.app.config:
                print('{}没有设置'.format(i))
                sys.exit(1)
        self.access_key_id = self.app.config['OSS_KEY_ID']
        self.access_key_secret = self.app.config['OSS_KEY_SECRET']
        self.endpoint = self.app.config['OSS_ENDPOINT']
        self.bucket_name = self.app.config['OSS_BUCKET']
        self.oss_domain = self.app.config.get('OSS_DOMAIN')

    @property
    def bucket(self):
        return oss2.Bucket(oss2.Auth(self.access_key_id, self.access_key_secret),
                           self.endpoint, self.bucket_name)

    # 下载一个文件对象
    def down_file_obj(self, file_name):
        try:
            file = self.bucket.get_object(file_name)
        except oss2.exceptions.NoSuchKey as e:
            logger.error('已经被删除了：request_id={0}'.format(e.request_id))
            return False
        else:
            return file

    # 针对excel文件的需求只是上传下载一下
    def download(self, file_name,file_save_name):
        try:
            self.bucket.get_object_to_file(file_name, file_save_name)
        except oss2.exceptions.NoSuchKey as e:
            logger.error('已经被删除了：request_id={0}'.format(e.request_id))
            return False
        else:
            return True

    # 上传字符串
    def up_str(self, file_name, file_str):
        self.bucket.put_object(file_name, file_str)
        return True

    # 上传文件对象
    def up_file_obj(self, file_name, file):
        self.bucket.put_object(file_name, file)
        return True

    def upload(self, file_name,file):
        with open(oss2.to_unicode(file), 'rb') as f:
            self.bucket.put_object(file_name, f)
        return True

    def delete(self, file_name):
        self.bucket.delete_object(file_name)
        return True

    @property
    def url_prefix(self):
        if self.oss_domain:
            return self.oss_domain
        return 'http://' + self.bucket_name + '.' + self.endpoint + '/'

    @staticmethod
    def file_name(suffix):
        time_str = str(time.time())
        random_str = str(random.randint(1, 10000))
        today = str(datetime.date.today())
        return 'lycra/' + today + '/' + time_str + random_str + '.' + suffix

    def copy_file(self, old, new):
        self.bucket.copy_object(self.bucket_name, old, new)
