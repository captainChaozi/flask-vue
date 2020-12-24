import os

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

basedir = os.path.abspath(os.path.dirname(__file__))

static_dir = os.path.join(basedir, 'static')
static_templates_dir = os.path.join(basedir, 'static/templates')



class Config:
    # flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))
    STATIC_DIR = static_dir
    # 微信
    WX_AUTH_URL = os.getenv('WX_AUTH_URL', '')
    WX_APP_ID = os.getenv('WX_APP_ID', '')
    WX_APP_SECRET = os.getenv('WX_APP_SECRET', '')


    # oss 配置
    OSS_KEY_ID = os.getenv('OSS_KEY_ID', "")
    OSS_KEY_SECRET = os.getenv('OSS_KEY_SECRET', "")
    OSS_BUCKET = os.getenv('OSS_BUCKET', "")
    OSS_ENDPOINT = os.getenv('OSS_ENDPOINT', "")
    OSS_DOMAIN = os.getenv('OSS_DOMAIN', "")

    # sqlalchemy配置
    user = os.getenv('DB_USER', 'postgres')
    pwd = os.getenv('DB_PASSWORD', '123456')
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = os.getenv('DB_PORT', '5432')
    db = os.getenv('DB_NAME', 'postgres')
    data = dict(user=user, pwd=pwd, host=host, port=port, db=db)
    con_str = 'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}'
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL') or con_str.format(**data)
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = os.getenv('REDIS_PORT', '6379')
    REDIS_DB = os.getenv('REDIS_DB', 0)
    REDIS_PWD = os.getenv('REDIS_PWD', '123456')
    _redis_url = "redis://:{pwd}@{host}:{port}/{db}". \
        format(pwd=REDIS_PWD, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)
    }
    # SCHEDULER_EXECUTORS = {
    #     'default': {'type': 'threadpool', 'max_workers': 20}
    # }
    #
    # SCHEDULER_JOB_DEFAULTS = {
    #     'coalesce': False,
    #     'max_instances': 3
    # }

    SCHEDULER_API_ENABLED = True if int(os.getenv('RUN_JOB',0))==0 else False




