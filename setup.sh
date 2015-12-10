#!/bin/bash

pip install --user virtualenv
python ~/.local/lib/python3.4/site-packages/virtualenv.py --no-site-packages ./virtualenv
virtualenv/bin/pip install pytest
virtualenv/bin/pip install pytest-cov
virtualenv/bin/pip install flask
virtualenv/bin/pip install flask-WTF
virtualenv/bin/pip install flask-login
virtualenv/bin/pip install flask-sqlalchemy
virtualenv/bin/pip install sqlalchemy-migrate
