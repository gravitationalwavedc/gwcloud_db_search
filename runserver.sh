#!/bin/bash
/src/venv/bin/python /src/production-manage.py migrate db_search;

/src/venv/bin/gunicorn gw_db_search.wsgi -b 0.0.0.0:8000
