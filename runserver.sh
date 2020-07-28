#!/bin/bash
/src/venv/bin/python /src/production-manage.py migrate;
/src/venv/bin/python /src/production-manage.py collectstatic --noinput;

/src/venv/bin/gunicorn gw_db_search.wsgi -b 0.0.0.0:8000
