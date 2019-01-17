from flask import Flask
import os, base64
import config

app = Flask(__name__)
from mp import callback,views

app.secret_key = config.secret_key

