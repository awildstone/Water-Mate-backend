"""Room view tests."""

# FLASK_ENV=production python3 -m unittest test_room_views.py

import os
from unittest import TestCase
from models import *

#set DB environment to test DB
os.environ['DATABASE_URL'] = 'postgresql:///water_mate_react_test'

from app import *

class TestRoomViews(TestCase):
    """A class to test room views in the app."""

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

        db.session.query(LightSource).delete()
        db.session.commit()

        db.session.query(Room).delete()
        db.session.commit()

        db.session.query(Collection).delete()
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

        self.user1.id = 10
        db.session.commit()

        self.user2 = User.signup(
            name='Kittenz Meow',
            email='kittenz@gmail.com',
            latitude='45.520247',
            longitude='-122.674195',
            username='kittenz',
            password='meowmeow')

        self.user2.id = 12
        db.session.commit()

        #set up test collections
        collection1 = Collection(id=1, name='Home', user_id=10)
        collection2 = Collection(id=2, name='My Collection', user_id=12)
        db.session.add_all([collection1, collection2])
        db.session.commit()

        #set up test rooms
        room1 = Room(id=1, name='Kitchen', collection_id=1)
        room2 = Room(id=2, name='Bedroom', collection_id=1)
        room3 = Room(id=3, name='Bedroom', collection_id=2)
        room4 = Room(id=4, name='Bathroom', collection_id=2)
        db.session.add_all([room1, room2, room3, room4])
        db.session.commit()

        #set up test light source
        light_source1 = LightSource(id=1, type='East', type_id=3, daily_total=8, room_id=1)
        db.session.add(light_source1)
        db.session.commit()

        #set up test plant
        plant1 = Plant(id=1, name='Hoya', image=None, user_id=10, type_id=37, room_id=1, light_id=1)
        db.session.add(plant1)
        db.session.commit()
    
    def tearDown(self):
        """Rollback any sessions."""
        db.session.rollback()
        db.session.remove()
