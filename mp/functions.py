#!/usr/bin/python
import MySQLdb
import os
from flask import Flask, render_template, redirect, request
import config

app = Flask(__name__)
app.config.from_object('config')

##variables
client_id = config.client_id
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

