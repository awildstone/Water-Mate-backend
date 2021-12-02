""" Plant Routes. """

from flask import Blueprint, request, jsonify
from models import db, Room, Plant, PlantType, WaterSchedule, WaterHistory
from .auth import auth_required
from uploader import Uploader
from datetime import datetime, timedelta

plant = Blueprint('plant', __name__)

####################
# Plant Routes
####################

@plant.route('/types/', methods=['GET'])
@auth_required
def get_planttypes(current_user):
    """Gets the list of plant types."""

    try:
        plant_types = PlantType.query.all()
        return jsonify({ "plant_types": plant_types }), 200

    except LookupError:
        return jsonify({ "msg": "Unable to get plant types." }), 404


@plant.route('/page/<int:page>/', methods=['GET'])
@auth_required
def get_plants(current_user, page):
    """Gets a paginated list of plants using query params."""

    items_per_page = 5
    room_id = request.args.get('room_id', None)
    user_id = request.args.get('user_id', None)

    if (room_id):
        room = Room.query.get_or_404(room_id)
        if (current_user.id == room.user_id):
            try:
                count = Plant.query.filter_by(room_id=room_id).all()
                plants = Plant.query.filter_by(room_id=room_id).order_by(Plant.name).paginate(page, items_per_page, False)
                return jsonify({ 'plants': plants.items, "count": len(count), "itemsPerPage": items_per_page }), 200
            except LookupError:
                return jsonify({ 'msg': "Unable to get plants." }), 404
        else:
            return jsonify({ "msg": "Not Authorized." }), 403

    if (user_id):
        if (current_user.id == int(user_id)):
            try:
                count = Plant.query.filter_by(user_id=user_id).all()
                plants = Plant.query.filter_by(user_id=user_id).paginate(page, items_per_page, False)
                return jsonify({ 'plants': plants.items, "count": len(count), "itemsPerPage": items_per_page }), 200
            except LookupError:
                return jsonify({ 'msg': "Unable to get plants." }), 404
        else:
            return jsonify({ "msg": "Not Authorized." }), 403

@plant.route('/count/<int:user_id>/', methods=['GET'])
@auth_required
def get_plants_count(current_user, user_id):
    """Gets the total count of plants for a user."""

    if current_user.id == user_id:
        try:
            plants = Plant.query.filter_by(user_id=current_user.id).all()
            return jsonify({ 'user_plant_count': len(plants) }), 200
        except LookupError:
            return jsonify({ 'msg': "Unable to get plants." }), 404
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@plant.route('/', methods=['POST'])
@auth_required
def add_plant(current_user):
    """Add a new plant to a room."""

    room_id = request.form['roomId']
    room = Room.query.get_or_404(room_id)

    try:
        if 'file' in request.files.keys():
            #if the image exists, securely upload to user's s3 bucket
            img = request.files['file']
            key = f'uploads/user/{current_user.id}/'
            connection = Uploader(current_user.id);
            url = connection.upload_image(key, img);

            new_plant = Plant(
                name=request.form['name'],
                image=url,
                user_id=current_user.id,
                type_id=request.form['plant_type'],
                room_id=room_id,
                light_id=request.form['light_source'])
        else:
            new_plant = Plant(
                name=request.form['name'],
                image=None,
                user_id=current_user.id,
                type_id=request.form['plant_type'],
                room_id=room_id,
                light_id=request.form['light_source'])
 
        room.plants.append(new_plant)
        db.session.commit()

        water_date = request.form['water_date'] if request.form['water_date'] else None
        Plant.create_waterschedule(new_plant, water_date)

        return jsonify({ "msg": "Success! Plant added." }), 201
    except Exception:
        return jsonify({ "msg": "Error adding plant!" }), 400


@plant.route('/<int:plant_id>/', methods=['GET'])
@auth_required
def get_plant(current_user, plant_id):
    """Get a plant by plant id."""

    plant = Plant.query.get_or_404(plant_id)

    if (current_user.id == plant.user_id):
        return jsonify({ "plant": plant }), 200
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@plant.route('/<int:plant_id>/', methods=['PATCH'])
@auth_required
def edit_plant(current_user, plant_id):
    """Edit a plant by id."""

    plant = Plant.query.get_or_404(plant_id)

    if (current_user.id == plant.user_id):
        try:
            if 'file' in request.files.keys():
                #if the image exists, securely upload to user's s3 bucket
                img = request.files['file']
                key = f'uploads/user/{current_user.id}/'
                connection = Uploader(current_user.id);
                url = connection.upload_image(key, img);

                #set the new plant url from the upload
                plant.image = url
            
            #update the rest of the applicable plant data
            plant.name = request.form['name']
            plant.type_id = request.form['plant_type']
            plant.light_id = request.form['light_source']
            db.session.commit()

            #reset the plant's water_schedule to reflect any changes in type or location but do not change the last water date.
            water_schedule = WaterSchedule.query.filter_by(plant_id=plant.id).first()
            plant_type = PlantType.query.get_or_404(plant.type_id)
            water_schedule.water_interval = plant_type.base_water
            water_schedule.next_water_date = water_schedule.water_date + timedelta(days=plant_type.base_water)
            db.session.commit()

            return jsonify({ "msg": "Success! Plant updated." }), 201

        except Exception:
            return jsonify({ "msg": "Error editing plant!" }), 400
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@plant.route('/<int:plant_id>/', methods=['DELETE'])
@auth_required
def delete_plant(current_user, plant_id):
    """Delete a plant by id."""

    plant = Plant.query.get_or_404(plant_id)

    if current_user.id == plant.user_id:
        if not '/images/succulents.png' in plant.image:
            # the img is hosted on s3 so we need to delete the image.
            #open a new connection with s3
            connection = Uploader(current_user.id);
            #attempt to delete the image
            connection.delete_image(plant.image)

        db.session.delete(plant)
        db.session.commit()
        return jsonify({ "msg": "Plant deleted." }), 200
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@plant.route('/history/<int:plant_id>/<int:page>/', methods=['GET'])
@auth_required
def get_history(current_user, plant_id, page):
    """Get paginated plant water history."""

    plant = Plant.query.get_or_404(plant_id)

    if current_user.id == plant.user_id:
        items_per_page = 5
        water_schedule = WaterSchedule.query.filter_by(plant_id=plant.id).first()
        count = WaterHistory.query.filter_by(water_schedule_id=water_schedule.id).all()
        history = WaterHistory.query.filter_by(water_schedule_id=water_schedule.id).paginate(page, items_per_page, False)
        return jsonify({ "history": history.items, "count": len(count), "itemsPerPage": items_per_page }), 200
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@plant.route('/water-schedule/<int:page>/', methods=['GET'])
@auth_required
def get_plants_to_water(current_user, page):
    """Get paginated plants to water filtered by user_id query param."""

    user_id = request.args.get('user_id', None)
    room_id = request.args.get('room_id', None)
    items_per_page = 8

    if (user_id):
        if current_user.id == int(user_id):
            count = Plant.query.join(Plant.water_schedule).filter(WaterSchedule.next_water_date <= datetime.today()).filter(Plant.user_id == current_user.id).all()

            plants = Plant.query.join(Plant.water_schedule).filter(WaterSchedule.next_water_date <= datetime.today()).filter(Plant.user_id == current_user.id).paginate(page, items_per_page, False)

            return jsonify({ "plants": plants.items, "count": len(count), "itemsPerPage": items_per_page }), 200
        else:
            return jsonify({ "msg": "Not Authorized." }), 403
    if (room_id):
        room = Room.query.get_or_404(room_id)
        if current_user.id == room.user_id:
            room_count = Plant.query.join(Plant.water_schedule).filter(WaterSchedule.next_water_date <= datetime.today()).join(Plant.room).filter(Plant.room_id == room_id).filter(Plant.user_id == current_user.id).all()

            plants = Plant.query.join(Plant.water_schedule).filter(WaterSchedule.next_water_date <= datetime.today()).join(Plant.room).filter(Plant.room_id == room_id).filter(Plant.user_id == current_user.id).paginate(page, items_per_page, False)
            
            return jsonify({ "plants": plants.items, "count": len(room_count), "itemsPerPage": items_per_page }), 200
        else:
            return jsonify({ "msg": "Not Authorized." }), 403
            