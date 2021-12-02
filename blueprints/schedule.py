""" Schedule Routes. """

from flask import Blueprint, g, request, jsonify
from models import db, WaterSchedule, PlantType, Plant, LightSource
from .auth import auth_required
from datetime import datetime, timedelta

schedule = Blueprint('schedule', __name__)

####################
# Schedule Routes
####################

@schedule.route('/<int:schedule_id>/', methods=['PATCH'])
@auth_required
def edit_waterschedule(current_user, schedule_id):
    """Edit a plant's water schedule via the schedule id. 
    Editing a water schedule will toggle the plant's water schedule 
    between manual mode or algorithm mode. If the schedule is set to manual 
    intervals it will not adjust for seasonal changes."""

    data = request.get_json()
    water_schedule = WaterSchedule.query.get_or_404(schedule_id)
    plant = Plant.query.get_or_404(water_schedule.plant_id)

    if current_user.id == plant.user_id:
        water_schedule.manual_mode = data['manual_mode']
        water_schedule.water_interval = int(data['water_interval']) if data['manual_mode'] == False else int(data['manual_water_interval'])
        water_schedule.next_water_date = water_schedule.water_date + timedelta(days=water_schedule.water_interval)
        db.session.commit()
        return jsonify({ "msg": "Success! Water Schedule updated." }), 200
    
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@schedule.route('/<int:schedule_id>/water/', methods=['POST'])
@auth_required
def water_plant(current_user, schedule_id):
    """Waters a plant by water schedule id, updates the water schedule and creates a record in the water schedule history table."""

    data = request.get_json()
    water_schedule = WaterSchedule.query.get_or_404(schedule_id)
    plant = Plant.query.get_or_404(water_schedule.plant_id)
    notes = data['notes'] if data else ''
    snooze_days = 0

    if (current_user.id == plant.user_id):
        try:
            #if the schedule is set to manual mode
            if water_schedule.manual_mode == True:
                water_schedule.water_date = datetime.today()
                water_schedule.next_water_date = datetime.today() + timedelta(days=water_schedule.water_interval)
                WaterSchedule.create_water_history_record(water_schedule, water_schedule.water_date, snooze_days, notes, plant.id, water_schedule.id)
              
                return jsonify({ "msg": "Success! Plant water schedule updated." }), 201
            
            #the water schedule is not set to manual mode
            else:
                plant_light_source = LightSource.query.get_or_404(plant.light_id)
                plant_type = PlantType.query.get_or_404(plant.type_id)

                #if light source is artifical, just update the next water date and add the history record
                if plant_light_source.type == 'Artificial':
                    water_schedule.next_water_date = datetime.today() + timedelta(days=water_schedule.water_interval)
                    WaterSchedule.create_water_history_record(water_schedule, datetime.today(), snooze_days, notes, plant.id, water_schedule.id);
                 
                    return jsonify({ "msg": "Success! Plant water schedule updated." }), 201
                
                #if the light source is natural, we need to calculate the next_water_date using the solar & water calculators
                new_water_interval = WaterSchedule.calculate_next_water_date(current_user, plant_type, water_schedule, plant_light_source.type)
               
                water_schedule.water_interval = new_water_interval
                water_schedule.water_date = datetime.today()
                water_schedule.next_water_date = datetime.today() + timedelta(days=new_water_interval)
                
                WaterSchedule.create_water_history_record(water_schedule, water_schedule.water_date, snooze_days, notes, plant.id, water_schedule.id)
             
                return jsonify({ "msg": "Success! Plant water schedule updated." }), 201

        except Exception:
            return jsonify({ "msg": "Error watering plant, please try again." }), 400
    
    else:
        return jsonify({ "msg": "Not Authorized." }), 403


@schedule.route('/<int:schedule_id>/snooze/', methods=['POST'])
@auth_required
def snooze_plant(current_user, schedule_id):
    """Snoozes a plant's water schedule for num_days, via the water schedule id.
    Updates the plant's water schedule and adds a record to the water history table indicating the plant was snoozed."""

    data = request.get_json()
    water_schedule = WaterSchedule.query.get_or_404(schedule_id)
    plant = Plant.query.get_or_404(water_schedule.plant_id)
    notes = data['notes'] if data else ''

    if (current_user.id == plant.user_id):
        try:
            #eventually this can be a user input, for now it is 3
            snooze_days = 3
            water_schedule.next_water_date = datetime.today() + timedelta(days=snooze_days)
            WaterSchedule.create_water_history_record(water_schedule, water_schedule.water_date, snooze_days, notes, plant.id, water_schedule.id)

            return jsonify({ "msg": "Success! Plant water schedule updated." }), 201

        except Exception:
            return jsonify({ "msg": "Error snoozing plant, please try again." }), 400

    else:
        return jsonify({ "msg": "Not Authorized." }), 403
        