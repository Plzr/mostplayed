from mp import app
from flask import Flask, render_template, redirect, request,session
import sys
import config
import requests
import json
import db
from datetime import datetime
from functions import db_insert,db_select
import base64
import os

app.config.from_object('config')
client_id = config.client_id




@app.route('/callback')
def process():
	
	if request.args.get('error'):
		return request.args.get('error')
	code = request.args.get('code')
	state = request.args.get('state')

	
	#################get the access token
	print 'Getting the access token'
	post_url = 'https://accounts.spotify.com/api/token'
	grant_type = 'authorization_code'
	callback_url = 'http://127.0.0.1:5000/callback'
	authorization = config.authorization

	post = {'redirect_uri':callback_url,'code':code,'grant_type':grant_type}
	headers = {'Authorization':authorization,'Accept':'application/json','Content-Type': 'application/x-www-form-urlencoded'}
	#headers = {'Authorization' + authorization, 'Accept:application/json','Content-Type: application/x-www-form-urlencoded'}
	
	r = requests.post(post_url, headers=headers,data=post)
	auth_json = json.loads(r.text)
	access_token = 'Bearer ' + auth_json['access_token']

	
	################get my details - create the user if needed
	print 'Getting the users details'
	me_headers = {'Authorization':access_token}
	me_post = {}
	me_url = 'https://api.spotify.com/v1/me'
	
	r_me = requests.get('https://api.spotify.com/v1/me',headers=me_headers)
	r_me_json = json.loads(r_me.text)

	user_id = r_me_json['id'].encode('utf-8')
	email = r_me_json['email'].encode('utf-8')
	now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	if 'ref_code' in session:
		referall_code = session['ref_code']
	else:
		referall_code = ''

	the_key = base64.b64encode(user_id + referall_code)
	
	try:
		db_insert("INSERT INTO user (user_id,email,join_date,last_visit,source,ref_code,the_key) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE last_visit=VALUES(last_visit);",(user_id,email,now,now,'new',referall_code,the_key))
		print "Inserted user"
	except Exception as e:
		print e


	###check if user has a pl in the DB already
		###yes = get pl id
		###no = create a new playlist

	if 'ref_code' in session:
		playlist_id = session['ref_code']
		print "Found a session: " + playlist_id
	#no referrer to check to see if they have an existing playlist
	else:
		# check_pl = db_select("SELECT playlist_id FROM participation WHERE user_id=%s",(user_id,))
		# data_check_pl = check_pl.fetchall()
	
		# for row in data_check_pl:
		# 	playlist_id = str(row[0])
		# 	print playlist_id
		print "no referrer was found so creating a new playlist"
			#playlist_id = '3klEOHTrLICmHtRvWwwOXh'
	try: 
		playlist_id
	except NameError:
		print "no playlist found"
		#return "no playlist found"

		#now create a collaborative playlist
		cp_headers = tt_headers = {'Authorization':access_token,'Content-Type': 'application/x-www-form-urlencoded'}
		cp_post = {'name': user_id + ' Most Played Bangers','public':'false','collaborative':'true'}
		cp_url = 'https://api.spotify.com/v1/users/' + user_id + '/playlists'
		r_cp = requests.post(cp_url,headers=cp_headers,data=json.dumps(cp_post))
		
		print r_cp.status_code

		if str(r_cp.status_code) !='201':
			print r_cp.json()

			return "It didnt work yo - try again"

		r_cp_json = r_cp.json()
		playlist_id = r_cp_json['id']
	


	the_key = base64.b64encode(user_id + playlist_id)
	db_insert("INSERT INTO participation (user_id,playlist_id,the_key) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE the_key=VALUES(the_key)",(user_id,playlist_id,the_key))




	##############get the users top tracks
	print "Getting the users top tracks"
	tt_headers = {'Authorization':access_token}
	tt_post = {}
	tt_url = 'https://api.spotify.com/v1/me/top/tracks?limit=50&time_range=long_term'
	r_tt = requests.get(tt_url,headers=tt_headers)
	tt_json = r_tt.json()
	#print tt_json
	
	##iterate through all the tracks and get them into a list
	tracks_list = []
	tracks = []
	for x in xrange(0,tt_json['limit']):

		track_name = tt_json['items'][x]['name']
		track_id = tt_json['items'][x]['id']
		track_uri = tt_json['items'][x]['uri']
		track_popularity = tt_json['items'][x]['popularity']
		#print track_name
		#print track_uri

		tracks_list.append(track_uri.encode("utf-8"))
		tracks.append(track_name.encode("utf-8"))

	
	##this is for the playlist
	print "Now adding to playlist"
	
	pl_url = 'https://api.spotify.com/v1/users/' + user_id + '/playlists/' + playlist_id + '/tracks'
	pl_public_url = 'https://open.spotify.com/user/' + user_id + '/playlist/' + playlist_id
	add_headers = {'Authorization':access_token,'Content-Type':'application/json'}
	add_post = {'uris':tracks_list}
	#print add_post

	r_add = requests.put(pl_url,headers=add_headers,data=json.dumps(add_post))
	print r_add.json()

	if 'ref_code' in session:
		session.pop('ref_code', None)

	
	return render_template('done.html',pl_url=pl_public_url,tracks=tracks,ref_code=playlist_id)

