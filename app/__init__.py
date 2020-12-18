import datetime

from flask import Flask
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.dialects.postgresql import JSONB

from config import Config
from utils import Model, RedisCache, get_user, get_group, get_tenant, get_user_name, get_group_name, generate_id, \
    formatter, CJsonEncoder
from flask_restful import Api
from flask.logging import default_handler


db = SQLAlchemy(model_class=Model)
redis = RedisCache()
default_handler.setFormatter(formatter)
ma = Marshmallow()
apscheduler = APScheduler()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['RESTFUL_JSON'] = {'cls':CJsonEncoder}
    redis.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    apscheduler.init_app(app)
    apscheduler.start(paused=Config.SCHEDULER_API_ENABLED)
    api = Api(app)
    from app.url_map import register
    register(api)

    return app


def get_session():
    return db.create_scoped_session(options={'autocommit': True,
                                             'autoflush': False})


class TimestampMixin(object):
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    modify_time = db.Column(db.DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)


class DataPermissionMixin(object):
    user_id = db.Column(db.String(50), nullable=True, default=get_user)
    group_id = db.Column(db.String(50), default=get_group)
    tenant_id = db.Column(db.String(50), default=get_tenant)
    create_user = db.Column(db.String(50), default=get_user_name)
    create_group = db.Column(db.String(50), default=get_group_name)


class SoftDeleteMixin(object):
    is_delete = db.Column(db.Integer, default=0)


class IdMixin(object):
    id = db.Column(db.String(50), primary_key=True, unique=True, default=generate_id)
    extend = db.Column(JSONB, default=dict())


class MainMixIn(IdMixin, TimestampMixin, SoftDeleteMixin):
    # tenant_id = db.Column(db.String(20),default=get_tenant)
    pass


class AllMixIn(MainMixIn, DataPermissionMixin):
    pass
