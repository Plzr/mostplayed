#!/usr/bin/python
activate_this = '/var/www/mostplayed/mp/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/mostplayed")
sys.path.insert(0,"/var/www/mostplayed/mp")

from mp import app as application
application.secret_key = 'Add your secret key'
