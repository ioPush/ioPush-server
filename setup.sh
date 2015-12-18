#!/bin/bash

pip install --user virtualenv
python ~/.local/lib/python3.4/site-packages/virtualenv.py --no-site-packages ./virtualenv
virtualenv/bin/pip install -r requirements.txt
chmod 775 misc
./db_create.py
chmod 771 misc/ioPush.db
chgrp www-data misc

