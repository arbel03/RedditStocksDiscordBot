from datetime import datetime

import pytest
from sqlalchemy import select

from ..database import Database
from ..datafeed import DataFeed
from .sentiment import Sentiment
from .body import Body


@pytest.fixture(scope="function")
def database(request):
    """Create SQLAlchemy engine to memory"""
    database = Database.initialize(test=True)

    def finalizer():
        """Drop the database at the end of the fixture"""
        return

    request.addfinalizer(finalizer)
    return database


# For more info about ORM: https://docs.sqlalchemy.org/en/14/tutorial/orm_data_manipulation.html
def test_create_body(database):
    body1 = Body(content="$TSLA and $AMC is the best stock!", 
        creation_datetime=datetime.now(), 
        datafeed=DataFeed.Enum.Reddit.value, 
        ticker="TSLA",
        sentiment=Sentiment())
    database.add_body(body1)

    all_bodies = database.get_session().execute(select(Body)).all()
    assert len(all_bodies) == 1
