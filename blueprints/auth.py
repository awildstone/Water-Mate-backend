""" Auth Routes. """

from functools import wraps
from flask import Blueprint, request
from flask.json import jsonify
from sqlalchemy.exc import IntegrityError
from models import db, User
from location import UserLocation
from uploader import Uploader

auth = Blueprint('auth', __name__)

####################
# Authentication
# Routes
####################

@auth.teardown_request
def teardown_request(exception):
    if exception:
        db.session.rollback()
    db.session.remove()

def auth_required(f):
    """This decorator function confirms there is a valid token in the request header before the request is processed."""
    @wraps(f)
    def decorator(*args, **kwargs):

       token = None
       if 'x-access-token' in request.headers:
           token = request.headers['x-access-token']
 
       if not token:
           return jsonify({'msg': 'A valid token is missing.'}), 401

       try:
           current_user = User.decode_token(token)
           
       except:
           return jsonify({'msg': 'Token is invalid. Please try again.'}), 401
 
       return f(current_user, *args, **kwargs)
    return decorator


####################
# Signup/Login/Token
# Routes
####################

@auth.route('/signup/', methods=['POST'])
def signup():
    """Get a user's geolocation and signup a new user. Authenticates a new user and returns a token."""

    if request.method == 'POST':
        data = request.get_json()

        city = data['city']
        state = data['state']
        country = data['country']
        name = data['name']
        email = data['email']
        username = data['username']
        password = data['password']

        #try to get coordinates data
        user_location = UserLocation(city=city, state=state, country=country)
        coordinates = user_location.get_coordinates()

        if coordinates:
            #try to create a new user account
            try:
                new_user = User.signup(
                    name=name,
                    email=email,
                    latitude=coordinates['lat'],
                    longitude=coordinates['lng'],
                    username=username,
                    password=password
                )
                db.session.commit()

                #try to create a new bucket for this user
                connection = Uploader(new_user.id)
                connection.create_bucket()

                if new_user:
                    token = User.create_access_token(new_user)
                    refresh_token = User.create_refresh_token(new_user)
                return jsonify({ "token": token, "refreshToken": refresh_token }), 201

            except IntegrityError:
                return jsonify({ "msg": "Please choose a different username." }), 403
        else:
            return jsonify({ "msg": "There was an error fetching your geolocation. Please check the spelling of your City, State, or Country and try again." }), 403
    

@auth.route('/login/', methods=['POST'])
def login():
    """Login an existing user. Authenticates a user and returns a token."""

    if request.method == 'POST':

        data = request.get_json()
        username = data['username']
        password = data['password']

        user = User.authenticate(username=username, password=password)

        if user:
            token = User.create_access_token(user)
            refresh_token = User.create_refresh_token(user)
            return jsonify({ "token": token, "refreshToken": refresh_token }), 201
    
    return jsonify({ "msg": "Not Authorized. Check your credentials and try again." }), 403


@auth.route('/token/refresh/', methods=['POST'])
def refresh():
    """Confirms a refresh token is in the request header & validates the refresh token. Creates a new auth token if the refresh token is valid.
    If the refresh token is invalid then an InvalidSignatureError will be thrown. """

    current_refresh_token = None

    if 'x-refresh-token' in request.headers:
           current_refresh_token = request.headers['x-refresh-token']

    if not current_refresh_token:
        return jsonify({'msg': 'A valid token is missing.'}), 401

    try:
        user = User.decode_refresh_token(current_refresh_token)
        auth_token = User.create_access_token(user);
        return jsonify({ "token": auth_token }), 201
              
    except:
        return jsonify({'msg': 'Token is invalid.'}), 401
