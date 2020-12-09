import redis
from datetime import datetime
import json

from utils.tools.json_encoder import CJsonEncoder


class RedisCache(object):
    """ Redis操作函数 """

    def __init__(self):
        self.r = None
        self.app = None

    def init_app(self, app):
        self.app = app
        self.connect()

    def connect(self):
        with self.app.app_context():
            pool = redis.ConnectionPool(host=self.app.config['REDIS_HOST'],
                                        port=self.app.config['REDIS_PORT'],
                                        db=self.app.config['REDIS_DB'],
                                        password=self.app.config['REDIS_PWD'],
                                        decode_responses=True)
            self.r = redis.Redis(connection_pool=pool)

    def publish(self, channel, message):
        return self.r.publish(channel=channel, message=message)

    def listen(self, channel):
        pubsub = self.r.pubsub()
        pubsub.subscribe(channel)
        return pubsub.listen()

    def set(self, key, value, expired=None):
        if expired:
            if isinstance(expired, datetime):
                dif = expired - datetime.now()
                seconds = int(dif.total_seconds())
                if seconds < 0:
                    seconds = 0
                expired = seconds
            elif isinstance(expired, int):
                expired = expired
            else:
                expired = None
        value = json.dumps(value, cls=CJsonEncoder)
        self.r.set(key, value, ex=expired)

    def get(self, key):
        res = self.r.get(key)
        if res:
            return json.loads(res)
        else:
            return None

    def ttl(self, key):
        return self.r.ttl(key)

    def expire(self, key, time):
        return self.r.expire(key, time)

    def sadd(self, name, value):
        return self.r.sadd(name, value)

    def smembers(self, name):
        return self.r.smembers(name)

    def delete(self, name):
        self.r.delete(name)
