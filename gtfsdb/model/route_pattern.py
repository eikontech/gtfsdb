import time

from sqlalchemy import Column, Sequence
from sqlalchemy.types import Integer, String

from gtfsdb import config
from gtfsdb.model.base import Base

import logging
log = logging.getLogger(__name__)


class RoutePattern(Base):
    datasource = config.DATASOURCE_DERIVED
    filename = None

    __tablename__ = 'route_patterns'

    route_pattern_id = Column(String(255), primary_key=True, index=True, nullable=False)
    route_id = Column(String(255), index=True, nullable=False)
    route_short_name = Column(String(255), nullable=False)
    direction_id = Column(String(255), nullable=False)
    trip_headsign = Column(String(255), nullable=False)
    representative_trip_id = Column(String(255), nullable=False)
    route_pattern_sort_order = Column(Integer, index=True, nullable=False)
    n_trips = Column(Integer, nullable=False)
    shape_id = Column(String(255), nullable=False)

    @classmethod
    def post_process(cls, db, **kwargs):
        log.debug('{0}.post_process'.format(cls.__name__))
        cls.populate(db.session)

    @classmethod
    def populate(cls, session):
        """
        Populate route_patterns table and update route_pattern_id values in trips table
        """

        from gtfsdb import Route, Trip
        from sqlalchemy import func

        start_time = time.time()
        try:
            q = session.query(
                Route.route_id.label("route_id"),
                Route.route_short_name.label("route_short_name"),
                Trip.direction_id.label("direction_id"),
                Trip.trip_headsign.label("trip_headsign"),
                Trip.shape_id.label("shape_id"),
                func.count(Trip.trip_id).label("n_trips"),
                func.row_number().over(partition_by=[Route.route_id, Trip.direction_id],
                                       order_by=func.count(Trip.trip_id).desc()
                                       ).label("route_pattern_sort_order")
            )
            q.select_from(Route)
            q = q.join(Trip, Route.route_id == Trip.route_id)
            q = q.group_by(Trip.shape_id)

            for row in q:
                trips = session.query(Trip).filter(
                    Trip.shape_id == row.shape_id)

                rp = RoutePattern()
                rp.route_pattern_id = f"{row.route_id}_{row.direction_id}_{row.route_pattern_sort_order}"
                rp.route_id = row.route_id
                rp.route_short_name = row.route_short_name
                rp.direction_id = row.direction_id
                rp.representative_trip_id = trips.first().trip_id
                rp.trip_headsign = row.trip_headsign
                rp.route_pattern_sort_order = row.route_pattern_sort_order
                rp.n_trips = row.n_trips
                rp.shape_id = row.shape_id
                session.add(rp)

                # Update route_pattern_id value in trips table
                trips.update({Trip.route_pattern_id: rp.route_pattern_id})

            session.commit()

        except Exception as e:
            log.error(e)
            session.rollback()

        finally:
            session.flush()
            session.close()
            processing_time = time.time() - start_time
            log.debug('{0}.populate ({1:.0f} seconds)'.format(
                cls.__name__, processing_time))
