from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, String, Date

from gtfsdb import config
from gtfsdb.model.base import Base


class VehicleTrip(Base):
    datasource = None
    filename = None

    __tablename__ = 'vehicles_trips'

    vehicle_id = Column(String(255), primary_key=True, index=True, nullable=False)
    trip_id = Column(String(255), primary_key=True, index=True, nullable=False)
    datetime = Column(Date(), primary_key=True, index=True, nullable=False)
