import logging

from manage import app
from utils import formatter

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
for handler in app.logger.handlers:
    handler.setFormatter(formatter)
app.logger.setLevel(gunicorn_logger.level)
