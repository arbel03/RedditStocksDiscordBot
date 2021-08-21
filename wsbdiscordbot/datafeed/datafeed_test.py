from . import DataFeed


def test_datafeed_enum():
    assert DataFeed.Enum is not None
    assert DataFeed.Enum.Reddit is not None