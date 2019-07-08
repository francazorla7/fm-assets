#! /usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, Response
from flask import request, make_response, current_app, jsonify, send_file
from flask_cors import CORS
import json
import pymongo
from pymongo import MongoClient
import random
from werkzeug.security import generate_password_hash, check_password_hash

class ConfigFMLogin(object):

	def __init__(self, config_file, using=False):

		super(ConfigFMLogin, self).__init__()

		self.session_key_active = True
		self.session_key_length = 16

		self.db_name = "test"
		self.collection_assets_name = "fm-assets"
		self.collection_allowed_requests_name = "fm-allowed-requests"
		self.collection_sessions_name = "fm-sessions"
		self.user_key = "email"

		if using:
			with open(config_file, "r") as f:

				f_json = json.load(f)
				print("Using {} as config file: \n{}".format(config_file, f_json))

# Create Flask's app
app = Flask(__name__)

# Use CORS
CORS(app)

# Load configuration
configuration = ConfigFMLogin("config.conf")

# Starts MongoDB
client = MongoClient()
db = client[configuration.db_name]

# Check if exists a session
def check_session_key(session_key, user_key):

	exists = db[configuration.collection_sessions_name].find_one({"session_key": session_key, configuration.user_key: user_key})
	if exists is None:
		return False

	return True

@app.route("/pic/<asset>/<session_key>", methods=["GET"])
def get_pic(asset, session_key):

	# Comprobamos que es una clave de sesión válida
	session_exists = db[configuration.collection_sessions_name].find_one({"session_key": session_key})

	if session_exists is None:

		r = {

			"error": "true",
			"text": "La clave de sesión es incorrecta."
		}
		resp = Response(json.dumps(r))
		resp.headers['Content-Type'] = 'application/json'
		resp.headers['Access-Control-Allow-Origin'] = '*'

		return resp

	# Comprobamos que la clave de sesion tiene permisos de acceso
	allowed_request_exists = db[configuration.collection_allowed_requests_name].find_one({

		"asset": asset,
		"session_key": session_key
		})

	if allowed_request_exists is None:

		r = {

			"error": "true",
			"text": "La sesión no tiene permiso para acceder al recurso."
		}
		resp = Response(json.dumps(r))
		resp.headers['Content-Type'] = 'application/json'
		resp.headers['Access-Control-Allow-Origin'] = '*'

		return resp

	# Obtenemos la ruta del recurso
	asset_exist = db[configuration.collection_assets_name].find_one({"asset": asset, "type": "image"})

	if asset_exist is None:

		r = {

			"error": "true",
			"text": "El recurso no existe o no es del tipo válido."
		}
		resp = Response(json.dumps(r))
		resp.headers['Content-Type'] = 'application/json'
		resp.headers['Access-Control-Allow-Origin'] = '*'

		return resp

	resp = make_response(send_file(asset_exist["path"], mimetype='image/jpg'))
	resp.headers['Access-Control-Allow-Origin'] = '*'
	return resp

if __name__ == '__main__':

	app.run("localhost", port=8888)