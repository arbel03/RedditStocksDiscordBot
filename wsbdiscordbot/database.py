import collections
from datetime import datetime
from contextlib import contextmanager

import cx_Oracle
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from .model import Base, Body, Ticker
from .util import is_test_mode, read_config


class Database:
    def __init__(self, connection_string, **kwargs):
        self.__engine = create_engine(
            connection_string,
            **kwargs)

    @classmethod
    def initialize(cls, **kwargs):
        database_config = read_config()["database"]

        connection_string = 'oracle://{user}:{password}@{sid}'.format(
            user=database_config["username"],
            password=database_config["password"],
            sid=database_config["dsn"])

        if is_test_mode():
            connection_string = 'sqlite:///:memory:'

        del kwargs['test']

        database = Database(connection_string, **kwargs)
        # Create all tables
        Base.metadata.create_all(database.__engine)
        return database

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = Session(self.__engine)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add(self, obj):
        with self.session_scope() as session:
            if isinstance(obj, collections.Iterable):
                for item in obj:
                    session.merge(item)
            else:
                session.merge(obj)
            session.commit()

    def get_all_tickers(self) -> list[Ticker]:
        with self.session_scope() as session:
            return session.query(Ticker).all()

    def get_ticker_mentions(self, 
        start: datetime = None, 
        end: datetime = None
    ):
        with self.session_scope() as session:
            return session.query(Body.ticker, func.count(Body.content)).group_by(Body.ticker).order_by(func.count(Body.content).desc())
