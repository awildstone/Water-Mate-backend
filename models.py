"""SQLAlchemy models for Water Mate."""

import os
from dataclasses import dataclass
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import jwt
from jwt import InvalidSignatureError
import uuid
import datetime
from datetime import timedelta
from water_calculator import WaterCalculator

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to the Flask app.
    This method is called in the Flask app.
    """

    db.app = app
    db.init_app(app)

####################
# Light Models
####################

@dataclass
class LightType(db.Model):
    """A Light Type has 9 potential types that are immutatble for users. 
    Types are Artificial, North, East, South, West, Northeast, Northwest, Southeast, Southwest. """

    __tablename__ = 'light_types'

    id: int
    type: str

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, unique=True, nullable=False)

@dataclass
class LightSource(db.Model):
    """A LightSource has a type, daily total (hours of light), room id, and location id."""

    __tablename__ = 'light_sources'
    __table_args__ = (db.UniqueConstraint('type_id', 'room_id'),)

    id: int
    type: LightType
    type_id: int
    daily_total: int
    room_id: int

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text, db.ForeignKey('light_types.type'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('light_types.id'), nullable=False)
    daily_total = db.Column(db.Integer, nullable=False, default=8) #default is 8 for cases where artificial light source is used
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='cascade'))

####################
# Schedule Models
####################
 
@dataclass
class WaterHistory(db.Model):
    """A Water History has a water date, snooze amount, notes, and a plant and water schedule id."""

    __tablename__ = 'water_history'

    id: int
    water_date: str
    snooze: int
    notes: str
    plant_id: int
    water_schedule_id: int

    id = db.Column(db.Integer, primary_key=True)
    water_date = db.Column(db.DateTime, nullable=False)
    snooze = db.Column(db.Integer)
    notes = db.Column(db.String(200), default='No notes added.', nullable=False,)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), nullable=False)
    water_schedule_id = db.Column(db.Integer, db.ForeignKey('water_schedules.id', ondelete='cascade'), nullable=False)

    @property
    def get_water_date(self):
        """Gets the current water_date and returns a string representation."""
        return self.water_date.strftime("%m/%d/%Y, %H:%M:%S")

@dataclass
class WaterSchedule(db.Model):
    """A Water Schedule has a next water date, plant id and holds a water history."""

    __tablename__ = 'water_schedules'

    id: int
    water_date: str
    next_water_date: str
    water_interval: int
    manual_mode: str
    plant_id: int
    water_history: WaterHistory

    id = db.Column(db.Integer, primary_key=True)
    water_date = db.Column(db.DateTime, nullable=False)
    next_water_date = db.Column(db.DateTime, nullable=False)
    water_interval = db.Column(db.Integer, nullable=False)
    manual_mode = db.Column(db.Boolean, nullable=False, default=False)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id', ondelete='cascade'), nullable=False)

    water_history = db.relationship('WaterHistory', backref='water_schedule', cascade='all, delete-orphan')

    @property
    def get_water_date(self):
        """Gets the current water_date and returns a string representation."""
        return self.water_date.strftime("%m/%d/%Y")
    
    @property
    def get_next_water_date(self):
        """Gets the current water_date and returns a string representation."""
        return self.next_water_date.strftime("%m/%d/%Y")
    
    @classmethod
    def calculate_next_water_date(cls, user, plant_type, water_schedule, light_type):
        """Creates a new Water Calculator instance with the user, plant type, water schedule and light type. Gets a solar forcast using user, plant and light data and calculates and returns the reccomended water interval for calculating the next water date for a plant."""

        water_calculator = WaterCalculator(
            user=user,
            plant_type=plant_type,
            water_schedule=water_schedule,
            light_type=light_type
        )

        new_water_interval = water_calculator.calculate_water_interval()

        return new_water_interval

    @classmethod
    def create_water_history_record(cls, water_schedule, water_date, snooze, notes, plant_id, water_schedule_id):
        """Creates a new water history record and appends the new history record to the schedule water history table."""

        water_schedule.water_history.append(
            WaterHistory(
                water_date=water_date,
                snooze=snooze if snooze else 0,
                notes=notes,
                plant_id=plant_id,
                water_schedule_id=water_schedule_id
            )
        )

        db.session.commit()

####################
# User Model
####################

@dataclass
class User(db.Model):
    """A User has an id, public id, name, email, latitude, longitude, username, and password.
    A user can have one or more collections.
    The User class authenticates an account and authorizes login tokens, and provides location data."""

    __tablename__ = 'users'

    id: int
    public_id: str
    name: str
    email: str
    latitude: str
    longitude: str
    username: str

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Numeric(8,6))
    longitude = db.Column(db.Numeric(9,6))
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

    collections = db.relationship('Collection', backref='user', cascade='all, delete-orphan')
    rooms = db.relationship('Room', backref='user')
    plants = db.relationship('Plant')

    def __repr__(self):
        return f'<User #{self.id}: {self.username}, {self.email}>'
    
    @property
    def get_coordinates(self):
        """Get and return this user's coordinates."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude
        }

    @classmethod
    def create_access_token(cls, user):
        """Generates a JWT for a newly created user or authenticated user. Token is valid for 30 minutes before authentication is required again. """

        token = jwt.encode({'wm_auth' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, os.environ.get('SECRET_KEY'), "HS256")
        return token
    
    @classmethod 
    def create_refresh_token(cls, user):
        """Generates a refresh token for updating an auth token. Token is valid for 14 days. """

        token = jwt.encode({'wm_refresh' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=14)}, os.environ.get('SECRET_KEY'), "HS256")
        return token
    
    @classmethod
    def decode_token(cls, token):
        """Confirms the authenticity of a JWT token from a request header. 
        If the token is valid, gets the user public_id from the token payload and returns the User object.
        If the token is invalid, throws InvalidSignatureError."""

        data = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
        current_user = User.query.filter_by(public_id=data['wm_auth']).first()
        return current_user
    
    @classmethod
    def decode_refresh_token(cls, token):
        """Confirms the authenticity of a JWT refresh token from a request header. 
        If the token is valid, gets the user public_id from the token payload and returns the User object.
        If the token is invalid, throws InvalidSignatureError."""

        data = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=["HS256"])
        current_user = User.query.filter_by(public_id=data['wm_refresh']).first()
        return current_user

    @classmethod
    def signup(cls, name, email, latitude, longitude, username, password):
        """Sign up a new user and hash the user password. 
        Return the new user with hashed password."""
        
        hashed_pwd = bcrypt.generate_password_hash(password, 8).decode('UTF-8')

        new_user = User(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            latitude=latitude,
            longitude=longitude,
            username=username,
            password=hashed_pwd
        )

        db.session.add(new_user)
        return new_user
    
    @classmethod
    def authenticate(cls, username, password):
        """Locate the user in the DB for the respective username/password.
        If the user is not found, or fails to authenticate return False."""

        user = User.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False
    
    @classmethod
    def changePassword(cls, user, curr_password, new_password):
        """ Validates that the current password is correct, and updates to new password if correct.
        Returns False if the current password fails to authenticate."""

        is_auth = user.authenticate(user.username, curr_password)

        if is_auth:
            new_hashed_pwd = bcrypt.generate_password_hash(new_password, 8).decode('UTF-8')
            user.password = new_hashed_pwd
            return user
        return False

####################
# Organization Models
####################

@dataclass
class Room(db.Model):
    """A Room has a name, a user id, a collection id, Lightsources, and holds plants and lightsources relationships."""

    __tablename__ = 'rooms'
    __table_args__ = (db.UniqueConstraint('collection_id', 'name'),)

    id: int
    name: str
    user_id: int
    collection_id: int
    lightsources: LightSource

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id', ondelete='cascade'), nullable=False)

    lightsources = db.relationship('LightSource', backref='room', cascade='all, delete-orphan')

@dataclass
class Collection(db.Model):
    """A Collection has a name, user id, and holds rooms."""

    __tablename__ = 'collections'
    __table_args__ = (db.UniqueConstraint('user_id', 'name'),)

    id: int
    name: str
    user_id: int
    rooms: Room

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))

    rooms = db.relationship('Room', backref='collection', cascade='all, delete-orphan')

####################
# Plant Models
####################

@dataclass
class PlantType(db.Model):
    """A PlantType has a name and base water schedule.
    A PlantType is immutable for Users and accessible to all Users to categorize plants."""

    __tablename__ = 'plant_types'

    id: int
    name: str
    base_water: int
    base_sunlight: int
    max_days_without_water: int

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    base_water = db.Column(db.Integer, nullable=False)
    base_sunlight = db.Column(db.Integer, nullable=False)
    max_days_without_water = db.Column(db.Integer, nullable=False)

    plants = db.relationship('Plant', backref='type')

@dataclass
class Plant(db.Model):
    """A plant has a name, image, user id, type id, room id/Room, light id/Light, and has room, lightsource and waterschedule relationships."""

    __tablename__ = 'plants'

    id: int
    name: str
    image: str
    user_id: int
    type_id: int
    room_id: int
    room: Room
    light_id: int
    light: LightSource
    water_schedule: WaterSchedule

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False, default='/images/succulents.png')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('plant_types.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    light_id = db.Column(db.Integer, db.ForeignKey('light_sources.id'), nullable=False)

    room = db.relationship('Room', backref='plants')
    water_schedule = db.relationship('WaterSchedule', backref='plant', cascade='all, delete-orphan')
    light = db.relationship('LightSource', backref='plants')

    @classmethod
    def create_waterschedule(cls, plant, date=None):
        """This is a helper function to create a Water Schedule for a newly added plant.
        Accepts a plant ORM object, sets water_date to provided water_date or current date if none provided.
        The initial water interval is set from plant's plant type base_water interval."""

        plant_type = PlantType.query.get_or_404(plant.type_id)

        if date:
            date_format = "%Y-%m-%d"
            date_object = datetime.datetime.strptime(date, date_format)

            plant.water_schedule.append(WaterSchedule(
                water_date=date_object,
                next_water_date=date_object + datetime.timedelta(days=plant_type.base_water),
                water_interval=plant_type.base_water,
                plant_id=plant.id
            ))

        else:
            plant.water_schedule.append(WaterSchedule(
                water_date=datetime.datetime.today(),
                next_water_date=datetime.datetime.today() + datetime.timedelta(days=plant_type.base_water),
                water_interval=plant_type.base_water,
                plant_id=plant.id
            ))

        db.session.commit()