from mp import app
from flask import Flask, render_template, redirect, request,session
import sys
import config
import requests
import json
import os
import base64



reload(sys)
sys.setdefaultencoding('utf-8')

#app = Flask(__name__)
app.config.from_object('config')
client_id = config.client_id



@app.route('/')
@app.route('/index')
def index():
	if request.args.get('ref_code'):
		ref_code = request.args.get('ref_code')
		session['ref_code'] = ref_code
		print session['ref_code']
	return render_template('index.html')

@app.route('/go')
def go():
	
	callback_url = 'http://127.0.0.1:5000/callback'
	base_url = 'https://accounts.spotify.com/en/authorize?client_id=' + client_id + '&response_type=code&redirect_uri=' + callback_url + '&scope=user-read-private%20user-read-email%20playlist-read-private%20user-follow-read%20user-library-read%20user-top-read%20playlist-modify-private%20playlist-modify-public&state=34fFs29kd09'
	return redirect(base_url,302)


