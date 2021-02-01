from ressources.db import db
from sqlalchemy import Column, Integer, String, Float

class Planet(db.Model):
    __tablename__ = 'planets' 
    planet_id = Column(Integer, primary_key = True)
    planet_name = Column(String)
    planet_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)