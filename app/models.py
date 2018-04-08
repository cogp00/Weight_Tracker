from app import db
from sqlalchemy.ext.automap import automap_base

db.reflect()
Base = automap_base(db.Model)

class Weight(db.Model):
    __tablename__ = 'weight'