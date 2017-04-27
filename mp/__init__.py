from flask import Flask
import os, base64

app = Flask(__name__)
from mp import callback,views,db

app.secret_key = base64.b64encode(os.urandom(24))
#print str(app.secret_key)

