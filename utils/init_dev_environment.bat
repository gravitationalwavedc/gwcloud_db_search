rem Set up python virtual env for auth module
cd ../src/
pip3 install virtualenv
virtualenv -p python3.8 venv

venv\Scripts\pip install -r requirements.txt

venv\Scripts\python development-manage.py migrate

pause
