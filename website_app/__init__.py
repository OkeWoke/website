from flask import Flask, jsonify, Response, url_for, send_from_directory, render_template, Markup, make_response, request, Blueprint
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth

from website_app.modules.database import GalleryTable, BlogTable, db
from website_app.modules.database_editor import Gallery as galDBE
from website_app.modules.database_editor import Blog as blogDBE

from PIL import Image
from datetime import date
import Utility as util
import os
import math
import werkzeug
import imghdr
import re
import json
import markdown

print("Working Dir: {0}".format(os.getcwd()))
try:
    with open('../config.json', 'r') as config_file:
        config_data = json.load(config_file)
except FileNotFoundError:
    print('No config file found, writing a default one')
    config_data = {'db': 'sqlite:///app.db', 'username': 'userNameHere', 'password': 'passwordHere', 'directory': ''}
    with open('../config.json', 'w') as config_file:
        json.dump(config_data, config_file, indent=4)
except

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config_data['db']
api = Api(app)
auth = HTTPBasicAuth()
db.init_app(app)
dbe = galDBE(db)
blogdbe = blogDBE(db)


"""
class GalleryAPI(Resource):
    def get(self):
        images = GalleryTable.query.all()[::-1]
        return jsonify([i.serialize() for i in images])
api.add_resource(GalleryAPI, '/api/')"""
#app.register_blueprint(routes)

# basic auth used, requires SSL for any security.


@auth.get_password
def get_password(username):
    if username == config_data['username']:
        return config_data['password']
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'Error': 'Unauthorized access'}), 401)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response

# Routes Import
from website_app.routes.blog_routes import *
from website_app.routes.gallery_routes import *
from website_app.routes.misc_routes import *

if __name__ == '__main__':
    app.run()
