""" User Routes. """


from flask import Blueprint, jsonify, request
from flask.json import jsonify
from models import db, User, Plant
from location import UserLocation
from sqlalchemy.exc import IntegrityError
from .auth import auth_required
from uploader import Uploader

user = Blueprint('user', __name__)

####################
# User Routes
####################

@user.route('/<user_id>/', methods=['GET'])
@auth_required
def get_user_data(current_user, user_id):
    """Get all data for the current authed user."""

    if (current_user.public_id == user_id):
        return jsonify({ 'user': current_user })
    
    return jsonify({ 'error': 'Unauthorized.' })


@user.route('/<int:user_id>/', methods=['PATCH'])
@auth_required
def edit_profile(current_user, user_id):
    """Edit a user's profile information."""

    data = request.get_json()

    if current_user.id == user_id:
        if User.authenticate(current_user.username, data['confirm_password']):
            try:
                user = User.query.get_or_404(user_id)
                user.name = data['name']
                user.username = data['username']
                user.email = data['email']
                db.session.commit()
                return jsonify({ "msg": "Success! Profile updated." }), 200
        
            except IntegrityError:
                return jsonify({ "msg": "Please choose a different username." }), 403
        else:
            return jsonify({ "msg": "Incorrect password." }), 403
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@user.route('/password/<int:user_id>/', methods=['PATCH'])
@auth_required
def edit_password(current_user, user_id):
    """Edit a user's password."""

    data = request.get_json()

    if current_user.id == user_id:
        if User.changePassword(current_user, data['old_password'], data['new_password']):
            db.session.commit()
            return jsonify({ "msg": "Success! Password updated." }), 200
        else:
            return jsonify({ "msg": "Incorrect old password." }), 403
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@user.route('/location/<int:user_id>/', methods=['PATCH'])
@auth_required
def edit_location(current_user, user_id):
    """Edit a user's geolocation."""

    data = request.get_json()

    if current_user.id == user_id:
        user_location = UserLocation(city=data['city'], state=data['state'], country=data['country'])
        coordinates = user_location.get_coordinates()

        if coordinates:
                current_user.latitude = coordinates['lat']
                current_user.longitude = coordinates['lng']
                db.session.commit()
                return jsonify({ "msg": "Success! Location updated." }), 200
        return jsonify({ "msg": "There was an error fetching your geolocation. Please check the spelling of your City or State/Country and try again."}), 400
    
    else:
        return jsonify({ "msg": "Not Authorized." }), 403
    

@user.route('/<int:user_id>/', methods=['DELETE'])
@auth_required
def delete_profile(current_user, user_id):
    """Delete a user's account and all data."""

    if current_user.id == user_id:
        try:
            #first delete all plants (all other orphan tables will cascade delete)
            user_plants = Plant.query.filter_by(user_id=current_user.id).all()
            for plant in user_plants:
                db.session.delete(plant)
                db.session.commit()

            #open a connection with s3
            connection = Uploader(current_user.id);
            #delete everything for this user from s3
            connection.delete_all();

            #try to delete the user
            db.session.delete(current_user)
            db.session.commit()

            return jsonify({'msg': 'Account permanently deleted.'}), 200

        except IntegrityError:
                return jsonify({ "msg": "There was a problem deleting your account." }), 400
        
    else:
        return jsonify({ "msg": "Not Authorized." }), 403
