#!/usr/bin/python
import MySQLdb
import os
from flask import Flask, render_template, redirect, request
import config
import requests
import json
import base64
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config')

##variables
#client_id = config.client_id
host = config.host
user = config.user
password = config.password
database = config.database


def db_select(query,params):

	db = MySQLdb.connect(host,user,password,database)
	cur = db.cursor()
	cur.execute(query,params)
	db.close()	
	return cur
	

def db_insert(query,params):
	
	db = MySQLdb.connect(host,user,password,database)
	cur = db.cursor()
	cur.execute(query,params)
	db.commit()
	db.close()
	return cur


def add_tracks(access_token,num_tracks,time_range,user_id,owner_id,playlist_id,now):
	print "Getting the users top tracks"
	tt_headers = {'Authorization':access_token}
	tt_post = {}
	tt_url = 'https://api.spotify.com/v1/me/top/tracks?limit=' + num_tracks + '&time_range=' + time_range
	r_tt = requests.get(tt_url,headers=tt_headers)
	tt_json = r_tt.json()
	print str(r_tt.status_code) + ' is the status code for the users top tracks'
	#print tt_json
	
	##iterate through all the tracks and get them into a list
	tracks_list = []
	tracks = []
	image_urls = []
	
	try:
		for x in xrange(0,tt_json['limit']):

			track_name = tt_json['items'][x]['name']
			track_id = tt_json['items'][x]['id']
			track_uri = tt_json['items'][x]['uri']
			track_popularity = tt_json['items'][x]['popularity']
			#if tt_json['items'][x]['images'][3]['url']:
			#	track_image = tt_json['items'][x]['images'][3]['url']
			#else:
			track_image = tt_json['items'][x]['album']['images'][1]['url']
			
			# print track_image
			# print track_name
			# print track_uri
			# print track_popularity

			tracks_list.append(track_uri.encode("utf-8"))
			tracks.append(track_name.encode("utf-8"))
			image_urls.append(track_image)
			the_key = base64.b64encode(user_id + track_id)

			#add to DB
			try:
				db_insert("INSERT INTO tracks (user_id,track_id,playlist_id,date,the_key,image_url) VALUES (%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE date=values(date)",(user_id,track_id,playlist_id,now,the_key,track_image))
				print "Inserted track " + track_id + ' for ' + user_id + ' into database'
			except Exception as e:
				print "Failed to insert track " + track_id
				print str(e)
	
	except Exception as e:
		print e
		print "No tracks to add!"

	
	##this is for the playlist
	print "Now adding to playlist " + playlist_id + " by " + owner_id
	
	pl_url = 'https://api.spotify.com/v1/users/' + owner_id + '/playlists/' + playlist_id + '/tracks'
	pl_public_url = 'https://open.spotify.com/user/' + owner_id + '/playlist/' + playlist_id
	add_headers = {'Authorization':access_token,'Content-Type':'application/json'}
	add_post = {'uris':tracks_list}
	#print add_post

	r_add = requests.put(pl_url,headers=add_headers,data=json.dumps(add_post))
	print r_add
	print r_add.json()
	return r_add,pl_public_url,playlist_id,tracks,image_urls


def create_playlist(access_token,user_id, title):
		cp_headers = {'Authorization':access_token,'Content-Type': 'application/x-www-form-urlencoded'}
		cp_post = {'name': title,'public':'true','collaborative':'false','description':'created at http://mp.soundshelter.net'}
		cp_url = 'https://api.spotify.com/v1/users/' + user_id + '/playlists'
		r_cp = requests.post(cp_url,headers=cp_headers,data=json.dumps(cp_post))
		
		print r_cp.status_code

		if str(r_cp.status_code) !='201':
			print r_cp.json()

			return "It didnt work yo - try again"
		r_cp_json = r_cp.json()
		playlist_id = r_cp_json['id']
		owner_id = r_cp_json['owner']['id']
		full_pl = base64.b64encode(owner_id + '/' + playlist_id)
		return owner_id,full_pl,playlist_id

def get_access_token(code):
	print 'Getting the access token'
	post_url = 'https://accounts.spotify.com/api/token'
	grant_type = 'authorization_code'
	#callback_url = 'http://127.0.0.1:5000/callback'
	callback_url = request.url_root + 'callback'
	authorization = config.authorization

	post = {'redirect_uri':callback_url,'code':code,'grant_type':grant_type}
	headers = {'Authorization':authorization,'Accept':'application/json','Content-Type': 'application/x-www-form-urlencoded'}
	#headers = {'Authorization' + authorization, 'Accept:application/json','Content-Type: application/x-www-form-urlencoded'}
	
	r = requests.post(post_url, headers=headers,data=post)
	auth_json = json.loads(r.text)
	try:
		access_token = 'Bearer ' + auth_json['access_token']
		print access_token
		return access_token
	except Exception as e:
		print "Something went wrong at the Spotify end - press back and try again"
		return "Something went wrong at the Spotify end - press back and try again"


def offline_update():
	return 'tbc'
