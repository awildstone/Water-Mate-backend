"""A file to seed the database with tables and LightType and PlantType data."""

# To seed a new DB, create a new postgres DB then save the DB name in app.py uri database identifier.
# Next, open ipython and first %run app.py then %run seed.py.

from csv import DictReader
from app import app
from models import db, LightType, PlantType

#create the tables
with app.app_context():
    db.create_all()

#now seed the DB with our shared data
artificial = LightType(type='Artificial')
north = LightType(type='North')
east = LightType(type='East')
south = LightType(type='South')
west = LightType(type='West')
northeast = LightType(type='Northeast')
northwest = LightType(type='Northwest')
southeast = LightType(type='Southeast')
southwest = LightType(type='Southwest')

db.session.add_all([artificial, north, east, south, west, northeast, northwest, southeast, southwest])
db.session.commit()

with open('generator/plant_types.csv') as plant_types:
    db.session.bulk_insert_mappings(PlantType, DictReader(plant_types))

db.session.commit()
