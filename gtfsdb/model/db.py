import logging
import sqlite3

from gtfsdb import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

log = logging.getLogger(__file__)


class Database(object):

    def __init__(self, **kwargs):
        """
        keyword arguments:
            is_geospatial: if database supports geo functions
            schema: database schema name
            tables: limited list of tables to load into database
            url: SQLAlchemy database url
        """
        #import pdb; pdb.set_trace()
        self.tables = kwargs.get('tables', None)
        url = kwargs.get('url')
        if not url:
            url = kwargs.get('database_url', config.DEFAULT_DATABASE_URL)
        self.url = url
        self.schema = kwargs.get('schema', config.DEFAULT_SCHEMA)
        self.is_geospatial = kwargs.get('is_geospatial', config.DEFAULT_IS_GEOSPATIAL)
        self.sorted_class_names = config.SORTED_CLASS_NAMES

    @property
    def classes(self):
        subclasses = self.get_base_subclasses()
        if self.tables:
            ret_val = [c for c in subclasses if c.__tablename__ in self.tables]
        else:
            ret_val = subclasses
        return ret_val

    @property
    def sorted_classes(self):
        classes = []
        for class_name in self.sorted_class_names:
            cls = next((c for c in self.classes if c.__name__ == class_name), None)
            if cls:
                classes.append(cls)
        return classes

    @classmethod
    def get_base_subclasses(cls):
        from gtfsdb.model.base import Base
        return Base.__subclasses__()

    @property
    def metadata(self):
        from gtfsdb.model.base import Base
        return Base.metadata

    def load_tables(self, **kwargs):
        """ load the sorted classes """
        for cls in self.sorted_classes:
            cls.load(self, **kwargs)

    def postprocess_tables(self, **kwargs):
        """ call the post-process routines on the sorted classes """
        do_postprocess = kwargs.get('do_postprocess', True)
        if do_postprocess:
            for cls in self.sorted_classes:
                cls.post_process(self, **kwargs)

    def create(self):
        """ drop/create GTFS database """
        for cls in self.sorted_classes:
            log.debug("create table: {0}".format(cls.__table__))
            try:
                cls.__table__.drop(self.engine, checkfirst=True)
            except:
                log.info("NOTE: couldn't *drop* table {0} (might not be a big deal)".format(cls.__table__))
            try:
                cls.__table__.create(self.engine)
            except Exception as e:
                log.info("NOTE: couldn't *create* table {0} (could be a big deal)\n{1}".format(cls.__table__, e))

    @property
    def dialect_name(self):
        return self.engine.url.get_dialect().name

    @property
    def is_geospatial(self):
        return self._is_geospatial

    @is_geospatial.setter
    def is_geospatial(self, val):
        self._is_geospatial = val
        for cls in self.classes:
            if val and hasattr(cls, 'add_geometry_column'):
                cls.add_geometry_column()

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, val):
        self._schema = val

        # TODO ... move to create() method
        try:
            if self._schema:
                from sqlalchemy.schema import CreateSchema
                self.engine.execute(CreateSchema(self._schema))
        except Exception as e:
            log.info("NOTE: couldn't create schema {0} (schema might already exist)\n{1}".format(self._schema, e))

        for cls in self.classes:
            cls.set_schema(self._schema)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, val):
        self._url = val
        self.engine = create_engine(val)
        if self.is_sqlite:
            sqlite3.register_adapter(str, lambda s: s.decode('utf8'))
            self.engine.connect().connection.connection.text_factory = str
        session_factory = sessionmaker(self.engine)
        self.session = scoped_session(session_factory)

    @property
    def is_postgresql(self):
        return 'postgres' in self.dialect_name

    @property
    def is_sqlite(self):
        return 'sqlite' in self.dialect_name

    @classmethod
    def factory(cls, **kwargs):
        """ helper method to open a Database object (and optionally create the tables in that Database) """
        db = cls(**kwargs)
        if kwargs.get('create'):
            db.create()
        return db

    @classmethod
    def factory_from_cmdline(cls, args):
        """ helper method to open a Database via a set of cmdline args object """
        kwargs = vars(args)
        return cls.factory(**kwargs)

    def prep_an_orm_class(self, orm_cls):
        self.prep_orm_class(orm_cls, self.schema, self.is_geospatial)

    @classmethod
    def prep_orm_class(cls, orm_cls, schema=None, is_geospatial=False):
        """
        helper method to ready an ORM class (see Base and it's children) according to this Database's settings
        :why?: sometimes you might have classes you want as part of a query, but you don't want those classes
        available in the Database.classes() or Database.sorted_classes(), since these tables are not being loaded, etc..
        """
        if is_geospatial and hasattr(orm_cls, 'add_geometry_column'):
            orm_cls.add_geometry_column()

        if schema:
            orm_cls.set_schema(schema)

    @classmethod
    def prep_gtfsdb_model_classes(cls, schema=None, is_geo=False):
        for c in cls.get_base_subclasses():
            cls.prep_orm_class(c, schema, is_geo)
