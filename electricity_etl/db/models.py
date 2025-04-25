from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Substation(Base):
    __tablename__ = "substations"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String, unique=True)
    circle = Column(String)
    division = Column(String)

class Feeder(Base):
    __tablename__ = "feeders"
    id = Column(Integer, primary_key=True)
    feeder_code = Column(String)
    name = Column(String)
    substation_id = Column(Integer, ForeignKey("substations.id"))

class DTR(Base):
    __tablename__ = "dtrs"
    id = Column(Integer, primary_key=True)
    dtr_code = Column(String)
    feeder_id = Column(Integer, ForeignKey("feeders.id"))
    capacity_kva = Column(Float)

class Consumer(Base):
    __tablename__ = "consumers"
    id = Column(Integer, primary_key=True)
    consumer_no = Column(String, unique=True)
    name = Column(String)
    dtr_id = Column(Integer, ForeignKey("dtrs.id"))
    category = Column(String)
    load_kw = Column(Float)

class Reading(Base):
    __tablename__ = "readings"
    id = Column(Integer, primary_key=True)
    entity_type = Column(String)  # 'feeder', 'dtr', or 'consumer'
    entity_id = Column(Integer)
    reading_kwh = Column(Float)
    reading_date = Column(Date)
