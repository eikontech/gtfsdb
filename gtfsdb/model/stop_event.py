from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, String, DateTime

from gtfsdb import config
from gtfsdb.model.base import Base


class StopEvent(Base):
    datasource = None
    filename = None

    __tablename__ = 'stop_events'

    vehicle_id = Column(String(255), primary_key=True, index=True, nullable=False)
    stop_id = Column(String(255), primary_key=True, index=True, nullable=False)
    stop_name = Column(String(255))
    arrival_time = Column(DateTime(), primary_key=True, index=True, nullable=False)
    departure_time = Column(DateTime(), nullable=False)
    boardings = Column(Integer)
    alightings = Column(Integer)
