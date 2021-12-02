""" Light Routes. """

from flask import Blueprint, jsonify, request
from flask.json import jsonify
from models import LightType, db, Room, LightSource
from sqlalchemy.exc import IntegrityError
from .auth import auth_required

light = Blueprint('light', __name__)

LIGHT_DICT = {
    "Artificial": 1,
    "North": 2,
    "East": 3,
    "South": 4,
    "West": 5,
    "Northeast": 6,
    "Northwest": 7,
    "Southeast": 8,
    "Southwest": 9   
}

####################
# Light Routes
####################

@light.route('/types/', methods=['GET'])
@auth_required
def get_lighttypes(current_user):

    try:
        light_types = LightType.query.all()
        return jsonify({ "light_types": light_types }), 200

    except LookupError:
        return jsonify({ "msg": "Unable to get light types." }), 404


@light.route('/', methods=['POST'])
@auth_required
def add_lightsource(current_user):
    """Add one or multiple light sources to a room."""

    print(request)
    data = request.get_json()
    print(data)
    room_id = data['roomId']
    print(room_id)
    room = Room.query.get_or_404(room_id)

    if current_user.id == room.user_id:
        try:
            for light in data:
                if data[light] == True:
                    room.lightsources.append(LightSource(type=light, type_id=LIGHT_DICT[light], room_id=room.id))
            
            db.session.commit()
            return jsonify({"msg": "Success! Lightsource(s) added."}), 201
        except IntegrityError:
            return jsonify({ "msg": "Lightsource already exists in room." }), 403
    else:
        return jsonify({ "msg": "Not Authorized." }), 403
    

@light.route('/<int:lightsource_id>/', methods=['DELETE'])
@auth_required
def delete_lightsource(current_user, lightsource_id):
    """Delete a lightsource from a room by lightsource_id. 
    Lightsources that have plants using them cannot
    be deleted."""

    lightsource = LightSource.query.get_or_404(lightsource_id)
    room = Room.query.get_or_404(lightsource.room_id)

    if current_user.id == room.user_id:
        try:
            db.session.delete(lightsource)
            db.session.commit()
            return jsonify({ "msg": "Room deleted." }), 200
        except IntegrityError:
            return jsonify({"msg": "You cannot delete a lightsource when plants are using it."}), 403
    else:
        return jsonify({ "msg": "Not Authorized." }), 403
        