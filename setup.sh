#!/bin/bash

pip install --user virtualenv
python3 ~/.local/lib/python3.4/site-packages/virtualenv.py --no-site-packages ./virtualenv
virtualenv/bin/pip install -r requirements.txt
chmod -R 775 misc
./db_create.py
chmod -R 771 misc/ioPush.db
chgrp -R www-data misc

