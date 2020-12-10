import logging

from flask import g,current_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell, Server
from app import create_app, db, get_session
from utils import formatter

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('runserver', Server(
    host='0.0.0.0', port=8000,use_debugger=True
))


def make_shell_context():
    return dict(db_session=get_session(), app=app)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

logger = logging.getLogger(__name__)

@app.before_request
def add_session():
    g.db_session = get_session()
    return

@app.route('/')
def hello():
    current_app.logger.debug("debug")
    current_app.logger.info("info")
    current_app.logger.warning("warning")
    current_app.logger.error("error")
    return 'hello,world'


@manager.command
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == "__main__":
    manager.run()

