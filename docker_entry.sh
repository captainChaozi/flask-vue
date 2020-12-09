#!/usr/bin/env bash

if [ "$RUN" = "celery" ]; then
    celery -A  task.celery worker -B --loglevel=warning
else
    gunicorn -b 0.0.0.0:8000 -w 9 manage:app --log-level debug
fi


