""" Collection Routes. """

from flask import Blueprint, jsonify, request
from models import db, Collection
from sqlalchemy.exc import IntegrityError
from .auth import auth_required

collection = Blueprint('collection', __name__)

####################
# Collection Routes
####################


@collection.route('/', methods=['GET'])
@auth_required
def get_collections(current_user):
    """Get all collections data for the current user."""

    collections = Collection.query.filter_by(
        user_id=current_user.id).order_by(Collection.id).all()
    return jsonify({'collections': collections}), 200


@collection.route('/<int:collection_id>/', methods=['GET'])
@auth_required
def get_collection(current_user, collection_id):
    """Get a collection by collection id."""

    collection = Collection.query.get_or_404(collection_id)
    if (current_user.id == collection.user_id):
        return jsonify({'collection': collection}), 200
    else:
        return jsonify({"msg": "Not Authorized."}), 403


@collection.route('/', methods=['POST'])
@auth_required
def add_collection(current_user):
    """Add a new collection."""

    data = request.get_json()

    new_collection = Collection(
        name=data['name'],
        user_id=current_user.id
    )

    try:
        current_user.collections.append(new_collection)
        db.session.commit()
        return jsonify({"msg": "Success! Collection added."}), 201

    except IntegrityError:
        return jsonify({"msg": "Duplicate collection name."}), 403


@collection.route('/<int:collection_id>/', methods=['PATCH'])
@auth_required
def edit_collection(current_user, collection_id):
    """Edit a collection by id."""

    collection = Collection.query.get_or_404(collection_id)
    data = request.get_json()

    if current_user.id == collection.user_id:
        try:
            collection.name = data['name']
            db.session.commit()
            return jsonify({"msg": "Success! Collection updated.", "collection": collection}), 200
        except IntegrityError:
            return jsonify({"msg": "Duplicate collection name."}), 403
    else:
        return jsonify({"msg": "Not Authorized."}), 403


@collection.route('/<int:collection_id>/', methods=['DELETE'])
@auth_required
def delete_collection(current_user, collection_id):
    """Delete a collection by id."""

    collection = Collection.query.get_or_404(collection_id)

    if current_user.id == collection.user_id:
        try:
            db.session.delete(collection)
            db.session.commit()
            return jsonify({"msg": "Collection deleted."}), 200
        except IntegrityError:
            return jsonify({"msg": "You cannot delete a collection that has plants!"}), 403
    else:
        return jsonify({"msg": "Not Authorized."}), 403
