""" Room Routes. """

from flask import Blueprint, request, jsonify
from models import db, Collection, Room
from sqlalchemy.exc import IntegrityError
from .auth import auth_required

room = Blueprint('room', __name__)

####################
# Room Routes
####################

@room.route('/', methods=['GET'])
@auth_required
def get_rooms(current_user):
    """Gets a filtered list of rooms using query params."""

    collection_id = request.args.get('collection_id', None)
    collection = Collection.query.get_or_404(collection_id)
    
    if (current_user.id == collection.user_id):
        try:
            rooms = Room.query.filter_by(collection_id=collection.id).order_by(Room.id).all()
            return jsonify({ 'rooms': rooms }), 200
        except LookupError:
            return jsonify({ 'msg': "Unable to get rooms." }), 404
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@room.route('/', methods=['POST'])
@auth_required
def add_room(current_user):
    """Add a new room."""

    data = request.get_json()
    collection = Collection.query.get_or_404(data['collectionId'])

    new_room = Room(
        name = data['name'],
        collection_id = data['collectionId'],
        user_id = current_user.id
    )

    try:
        collection.rooms.append(new_room)
        db.session.commit()
        return jsonify({ "msg": "Success! Room added." }), 201

    except IntegrityError:
        return jsonify({ "msg": "Duplicate room name." }), 403


@room.route('/<int:room_id>/', methods=['PATCH'])
@auth_required
def edit_room(current_user, room_id):
    """Edit a room by id."""

    data = request.get_json()
    room = Room.query.get_or_404(room_id)
    
    if current_user.id == room.user_id:
        try:
            room.name = data['name']
            db.session.commit()
            return jsonify({ "msg": "Success! Room updated.", "room": room }), 200
        except IntegrityError:
            return jsonify({ "msg": "Duplicate room name." }), 403
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@room.route('/<int:room_id>/', methods=['DELETE'])
@auth_required
def delete_room(current_user, room_id):
    """Delete a room by id."""

    room = Room.query.get_or_404(room_id)

    if current_user.id == room.user_id:
        try:
            db.session.delete(room)
            db.session.commit()
            return jsonify({ "msg": "Room deleted." }), 200
        except IntegrityError:
            return jsonify({"msg": "You cannot delete a room that has plants!"}), 403
    else:
        return jsonify({ "msg": "Not Authorized." }), 403
    