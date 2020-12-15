import datetime

from app import db,MainMixIn
from sqlalchemy.ext.hybrid import hybrid_property

class Demo(db.Model,MainMixIn):

    name = db.Column(db.String(10),comment='名字',info={'eg':'张三','des':'这是名字'})
    date = db.Column(db.Date,default=datetime.date.today)
    time = db.Column(db.DateTime,default=datetime.datetime.now)
    num = db.Column(db.DECIMAL(20,4),comment="数字")
    test = db.Column(db.String(10),nullable=False,info={'a':1,'b':2})

    @hybrid_property
    def hello(self):
        return 123

class DemoItem(db.Model,MainMixIn):

    demo_id = db.Column(db.String(50),db.ForeignKey('demo.id'))
    demo = db.relationship('Demo',backref = db.backref('items',lazy='dynamic'))
    name = db.Column(db.String(400))
    data = db.Column(db.Date)
    number = db.Column(db.Integer)
