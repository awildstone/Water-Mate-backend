"""Flask App for Water Mate."""

import os
from flask import Flask, jsonify
from models import connect_db
from custom_json_encoder import CustomJSONEncoder
# from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS

app = Flask(__name__)
#this encodes specific data into strings for JSON responses
app.json_encoder = CustomJSONEncoder
#this updates CORS policy so that 'Access-Control-Allow-Origin' headers can be on the same domain (for local server/development only)
CORS(app)

#import and register blueprint routes
from blueprints.auth import auth
app.register_blueprint(auth)

from blueprints.user import user
app.register_blueprint(user, url_prefix='/user')

from blueprints.collection import collection
app.register_blueprint(collection, url_prefix='/collection')

from blueprints.room import room
app.register_blueprint(room, url_prefix='/room')

from blueprints.light import light
app.register_blueprint(light, url_prefix='/light')

from blueprints.plant import plant
app.register_blueprint(plant, url_prefix='/plant')

from blueprints.schedule import schedule
app.register_blueprint(schedule, url_prefix='/schedule')

#set database uri identifier
uri = os.getenv('DATABASE_URL', 'postgresql:///water_mate_react')
if uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)

#set app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = uri
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False # for development only
# toolbar = DebugToolbarExtension(app) # for development only
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #Disables Flask file caching

#connect app to database
connect_db(app)

####################
# Error Handling
# Routes
####################

@app.errorhandler(404)
def page_not_found(e):
    """404 not found."""
    return jsonify({ "msg": "Not found." }), 404

@app.errorhandler(403)
def forbidden(e):
    """403 forbidden route."""
    return jsonify({ "msg": "Not authorized." }), 403