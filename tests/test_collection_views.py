"""Collection View Tests."""

# FLASK_ENV=production python3 -m unittest test_collection_views.py

import os
from dotenv import load_dotenv
from unittest import TestCase
from models import *

#set DB environment to test DB
os.environ['DATABASE_URL'] = 'postgresql:///water_mate_react_test'

from app import *

class TestCollectionViews(TestCase):
    """A class to test collection view route functionality in app."""

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
        collection2 = Collection(id=2, name='Work', user_id=10)
        db.session.add_all([collection1, collection2])
        db.session.commit()

        #add a test room
        room1 = Room(id=1, name='Kitchen', collection_id=1)
        db.session.add(room1)
        db.session.commit()
    
    def tearDown(self):
        """Rollback any sessions."""
        db.session.rollback()
        db.session.remove()
        