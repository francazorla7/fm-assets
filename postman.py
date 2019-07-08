# -*- coding: utf-8 -*-

import requests
import json
import pymongo
from pymongo import MongoClient

def post_login(email, password):

	headers = {'content-type': 'application/json'}

	params = {

		"email": email,
		"username": "",
		"name": "",
		"password": password
	}

	r = requests.post("http://localhost:9999/login", headers=headers, json=json.dumps(params))
	response = json.loads(r.content)

	return response

def post_logout(email, session_key):

	headers = {'content-type': 'application/json'}

	params = {

		"email": email,
		"session_key": session_key
	}

	r = requests.post("http://localhost:9999/logout", headers=headers, json=json.dumps(params))
	response = json.loads(r.content)

	return response

def get_pic(asset, session_key):

	r = requests.get("http://localhost:8888/pic/{}/{}".format(asset, session_key))

	try:
		response = json.loads(r.content)
	except:
		return "Image"

	return response

if __name__ == '__main__':

	# Añadimos un asset de ejemplo
	client = MongoClient()
	db = client["test"]
	db["fm-assets"].drop()
	db["fm-allowed-requests"].drop()

	login = post_login("francazorla7@hotmail.es", "test1234")
	print(login)

	# Creamos el recurso
	db["fm-assets"].insert_one({

		"asset": "hot_pic",
		"path": "res/vangaveeti-actress-naina-ganguly-hot-photos-9.jpg",
		"type": "image"
	})

	# Damos permiso
	db["fm-allowed-requests"].insert_one({

		"asset": "hot_pic",
		"session_key": login["session_key"]
	})

	print(get_pic("hot_pic", login["session_key"]))

	db["fm-assets"].delete_one({

		"asset": "hot_pic"
	})

	print(get_pic("hot_pic", login["session_key"]))

	#Quitamos permiso
	db["fm-allowed-requests"].delete_one({

		"asset": "hot_pic",
		"session_key": login["session_key"]
	})

	print(get_pic("hot_pic", login["session_key"]))

	print(post_logout(**login))