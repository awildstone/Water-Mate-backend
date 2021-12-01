"""Test Plant Views."""

# FLASK_ENV=production python3 -m unittest test_plant_views.py

import os
from io import BytesIO
# from csv import DictReader
from unittest import TestCase
from models import *
from datetime import datetime, timedelta

#set DB environment to test DB
os.environ['DATABASE_URL'] = 'postgresql:///water_mate_react_test'

from app import *

class TestPlantViews(TestCase):
    """A class to test plant views and functionality in the app."""

    def setUp(self):
        """Setup DB rows and clear any old data."""

        self.client = app.test_client()

        db.session.rollback()
        db.session.remove()

        #delete any old data from the tables
        db.session.query(WaterHistory).delete()
        db.session.commit()

        db.session.query(WaterSchedule).delete()
        db.session.commit()

        db.session.query(Plant).delete()
        db.session.commit()

        db.session.query(Collection).delete()
        db.session.commit()

        db.session.query(LightSource).delete()
        db.session.commit()

        db.session.query(Room).delete()
        db.session.commit()

        db.session.query(User).delete()
        db.session.commit()

        #set up test user accounts
        self.user1 = User.signup(
            name='Pepper Cat',
            email='peppercat@gmail.com',
            latitude='47.466748',
            longitude='-122.34722',
            username='peppercat',
            password='meowmeow')

        self.user1.id = 1000
        db.session.commit()

        self.user2 = User.signup(
            name='Kittenz Meow',
            email='kittenz@gmail.com',
            latitude='45.520247',
            longitude='-122.674195',
            username='kittenz',
            password='meowmeow')

        self.user2.id = 1200
        db.session.commit()

        #set up test collections
        collection1 = Collection(id=1, name='Home', user_id=1000)
        collection2 = Collection(id=2, name='My House', user_id=1200)
        db.session.add_all([collection1, collection2])
        db.session.commit()

        #set up test rooms
        room1 = Room(id=1, name='Kitchen', collection_id=1)
        room2 = Room(id=2, name='Bedroom', collection_id=2)
        db.session.add_all([room1, room2])
        db.session.commit()

        #set up test light sources
        light_source1 = LightSource(id=1, type='East', type_id=3, daily_total=8, room_id=1)
        light_source2 = LightSource(id=2, type='Southwest', type_id=9, daily_total=8, room_id=2)
        db.session.add_all([light_source1, light_source2])
        db.session.commit()
        
        #set up test plants
        plant1 = Plant(id=1, name='Hoya', image=None, user_id=1000, type_id=37, room_id=1, light_id=1)
        db.session.add(plant1)
        db.session.commit()

        #set up test water schedule
        ws1 = WaterSchedule(id=1, water_date=datetime(2021, 5, 1), next_water_date=datetime(2021, 5, 1) + timedelta(days=7), water_interval=7, plant_id=1)
        db.session.add(ws1)
        db.session.commit()
    
    def tearDown(self):
        """Rollback any sessions."""
        db.session.rollback()
        db.session.remove()

