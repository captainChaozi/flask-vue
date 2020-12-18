from app import get_session,apscheduler
from app.demo.model import Demo
def job(a,b):
    with apscheduler.app.app_context():
        db_session = get_session()
        c = db_session.query(Demo)
        # print(c.all())
    return a+b