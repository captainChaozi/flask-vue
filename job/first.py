from app import get_session,apscheduler,redis
from app.demo.model import Demo
def job(a,b):
    with apscheduler.app.app_context():
        db_session = get_session()
        c = db_session.query(Demo)
        # print(c.all())
        ss = redis.get('aa')
        redis.set('aa',1)
        s = redis.get('aa')
        print(s)
    return a+b