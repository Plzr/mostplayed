# from mp import app
import sys
#import config
import requests
import json
from datetime import datetime
from functions import db_insert,db_select,add_tracks,create_playlist,get_access_token,offline_update
import base64
import os


# app.config.from_object('config')
# client_id = config.client_id


#get everyone who has OAUTH details in the db AND their playlists
	#for each playlist
		#if oauth is out of date, email the user and get them to reauthenticate
		#else
			#get top tracks and add to playlist

query_get_playlists = '''SELECT p.playlist_id,p.time_range,user.email,user.the_key,p.user_id FROM participation p
JOIN user
ON p.user_id=user.user_id
WHERE user.the_key LIKE %s
#AND user.user_id='siquick'
GROUP BY p.playlist_id'''

get_playlists = db_select(query_get_playlists,('Bearer%',))

data_get_playlists = get_playlists.fetchall()

for row in data_get_playlists:
	playlist_id = row[0]
	time_range = row[1]
	email = row[2]
	access_token = row[3]
	user_id = row[4]
	owner_id = row[4]
	num_tracks = '50'
	now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	print 'Doing ' + time_range + ' for ' + user_id


	add = add_tracks(access_token,num_tracks,time_range,user_id,owner_id,playlist_id,now)
	print add[1]

	follow_url = '	https://api.spotify.com/v1/users/' + owner_id + '/playlists/' + playlist_id + '/followers'
	print follow_url + ' is going to be followed'
	follow_headers = {'Authorization':access_token,'Content-Type':'application/json'}
	follow_post = {'public': 'true'}
	r_follow = requests.put(follow_url,headers=follow_headers,data=follow_post)
	print r_follow
	#print r_follow.json()