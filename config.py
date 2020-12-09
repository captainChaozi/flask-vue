import os

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
    user = os.getenv('DB_USER', '')
    pwd = os.getenv('DB_PASSWORD', '')
    host = os.getenv('DB_HOST', '')
    port = os.getenv('DB_PORT', '')
    db = os.getenv('DB_NAME', '')
    data = dict(user=user, pwd=pwd, host=host, port=port, db=db)
    con_str = 'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}'
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL') or con_str.format(**data)
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', '')
    REDIS_PORT = os.getenv('REDIS_PORT', '')
    REDIS_DB = os.getenv('REDIS_DB', )
    REDIS_PWD = os.getenv('REDIS_PWD', '')
    _redis_url = "redis://:{pwd}@{host}:{port}/{db}". \
        format(pwd=REDIS_PWD, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)




