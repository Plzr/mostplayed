from mp import app
from flask import Flask, render_template, redirect, request,session
import sys
import config
import requests
import json
from datetime import datetime
from functions import db_insert,db_select,add_tracks,create_playlist,get_access_token,offline_update
import base64
import os


app.config.from_object('config')
client_id = config.client_id


@app.route('/callback')
def process():




	#print request.url_root

	if request.args.get('error'):
		return request.args.get('error')
	code = request.args.get('code')
	state = request.args.get('state')


	access_token = get_access_token(code)


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
		db_insert("INSERT INTO user (user_id,email,join_date,last_visit,source,ref_code,the_key) VALUES (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE last_visit=VALUES(last_visit), the_key=VALUES(the_key);",(user_id,email,now,now,'new',referall_code,access_token))
		print "Inserted user"
	except Exception as e:
		print e


	###check if user has a pl in the DB already
		###yes = get pl id
		###no = create a new playlist

	if 'ref_code' in session:
		playlist_id = session['ref_code']
		print "Found a session: " + playlist_id
		owner_id = user_id
		full_pl_exp = session['ref_code'].split('/')
		playlist_id =  full_pl_exp[1]
		owner_id = full_pl_exp[0]
	#no referrer to check to see if they have an existing playlist
	else:
		# check_pl = db_select("SELECT playlist_id FROM participation WHERE user_id=%s",(user_id,))
		# data_check_pl = check_pl.fetchall()

		# for row in data_check_pl:
		# 	playlist_id = str(row[0])
		# 	print playlist_id
		print "no referrer was found so creating a new playlist"
		print "no playlist found in the session"
		#return "no playlist found"

		#now create a collaborative playlist
		##############get the users top tracks

		if 'time_range' in session:
			time_range = session['time_range']
		else:
			time_range = 'short_term'

		if time_range =='short_term':
			time_range_title = 'This Month'
		elif time_range=='medium_term':
			time_range_title = 'Last Few Months'
		else:
			time_range_title = 'This Year and Beyond'
		title = 'Most Played: ' + time_range_title

		#check that there isn't a playlist already for this user on this time range
		check_for_pl = db_select("SELECT user_id,playlist_id FROM participation WHERE user_id=%s AND time_range=%s LIMIT 1",(user_id,time_range))
		if check_for_pl.rowcount==0:
			print "there were no results so we need to create a playlist"

			######create playlist
			create = create_playlist(access_token,user_id,title)

			owner_id = create[0]
			full_pl = create[1]
			playlist_id = create[2]

		else:
			print check_for_pl.rowcount
			print "There was a playlist"

			#get pl lists
			for row in check_for_pl:
				owner_id = row[0]
				playlist_id = row[1]

			full_pl = base64.b64encode(owner_id + '/' + playlist_id)

			print full_pl
			print "pl got"

			#update the name of the playlist if it exists
			up_headers = {'Authorization':access_token,'Accept':'application/json','Content-Type':'application/json'}
			up_post = {'name':title,'description':'Created at mp.soundshelter.net'}
			up_url = 'https://api.spotify.com/v1/users/' + owner_id + '/playlists/' + playlist_id
			r_up = requests.put(up_url,headers=up_headers,data=json.dumps(up_post))
			print up_url
			print up_headers
			print r_up
			print str(r_up.status_code) + ' is the update for the playlist name'


	full_pl = base64.b64encode(owner_id + '/' + playlist_id)
	the_key = base64.b64encode(user_id + playlist_id)
	db_insert("INSERT INTO participation (user_id,playlist_id,the_key,time_range) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE the_key=VALUES(the_key)",(user_id,playlist_id,the_key,time_range))



	#get the number of tracks the user wants to add
	if not session.get('num_tracks',None):
		num_tracks = '50'
	else:
		num_tracks = session['num_tracks']

	print num_tracks

	#get and add tracks to playlist
	add_done = add_tracks(access_token,num_tracks,time_range,user_id,owner_id,playlist_id,now)
	pl_public_url = add_done[1]
	tracks = add_done[3]
	playlist_id = add_done[2]
	image_urls = add_done[4]



	#####finally follow the playlist
	# follow_url = '	https://api.spotify.com/v1/users/' + owner_id + '/playlists/' + playlist_id + '/followers'
	# print follow_url + ' is going to be followed'
	# follow_headers = {'Authorization':access_token,'Content-Type':'application/json'}
	# follow_post = {'public': 'true'}
	# r_follow = requests.put(follow_url,headers=add_headers,data=json.dumps(add_post))
	# print r_follow
	# print r_follow.json()


	if 'ref_code' in session:
		session.pop('ref_code', None)


	return render_template('done.html',pl_url=pl_public_url,tracks=tracks,ref_code=full_pl,images=image_urls,title=title)

