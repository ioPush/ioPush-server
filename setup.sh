#!/bin/bash

pip install --user virtualenv
python ~/.local/lib/python3.4/site-packages/virtualenv.py --no-site-packages ./virtualenv
virtualenv/bin/pip install -r requirements.txt
mkdir misc

