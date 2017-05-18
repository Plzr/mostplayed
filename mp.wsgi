#!/usr/bin/python
import random

activate_this = '/var/www/mostplayed/mp/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/mostplayed")
# BASE_DIR = os.path.join(os.path.dirname(__file__))
# if BASE_DIR not in sys.path:
#     sys.path.append(BASE_DIR)

from mp import app as application
application.secret_key = str(base64.b64encode(os.urandom(24)))

