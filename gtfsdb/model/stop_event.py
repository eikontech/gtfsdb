from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, String, DateTime

from gtfsdb import config
from gtfsdb.model.base import Base


class StopEvent(Base):
    datasource = None
    filename = None

    __tablename__ = 'stop_events'

    trip_id = Column(String(255), primary_key=True, index=True, nullable=False)
    stop_id = Column(String(255), nullable=False)
    stop_sequence = Column(Integer, primary_key=True, index=True, nullable=False)
    stop_name = Column(String(255))
    vehicle_id = Column(String(255), nullable=False)
    arrival_datetime = Column(DateTime(), primary_key=True, index=True, nullable=False)
    departure_datetime = Column(DateTime(), nullable=False)
    boarding = Column(Integer)
    alighting = Column(Integer)
