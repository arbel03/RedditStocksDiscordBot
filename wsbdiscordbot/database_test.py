import pytest

import traceback

from .database import Database


def test_connection():
    try:
        Database.initialize(test=True)
    except BaseException as ex:
        pytest.fail(str(ex))
        traceback.print_exc()