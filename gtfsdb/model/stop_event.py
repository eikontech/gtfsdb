from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base


class StopEvent(Base):
    datasource = None
    filename = None

    __tablename__ = 'stop_events'

    id = Column(Integer, Sequence(None, optional=True), primary_key=True, nullable=True)
    vehicle_id = Column(String(255), nullable=False)
    stop_id = Column(String(255), nullable=False)
    stop_name = Column(String(255))
    stop_sequence = Column(Integer, nullable=False)
    arrival_time = Column(String(255), nullable=False)
    departure_time = Column(String(255), nullable=False)
    boardings = Column(Integer)
    alightings = Column(Integer)
