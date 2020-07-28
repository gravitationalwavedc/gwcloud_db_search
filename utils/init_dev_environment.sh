echo Set up python virtual env for db search module
cd ../src/
virtualenv -p python3.8 venv

venv/bin/pip install -r requirements.txt

venv/bin/python development-manage.py migrate


