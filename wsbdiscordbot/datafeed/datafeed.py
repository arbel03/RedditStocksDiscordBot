from enum import Enum
from datetime import datetime
from abc import abstractmethod


FETCH_LIMIT = 10


class DataFeedMetaClass(type):
    def get_subclasses(self):
        items = [(subcls.__name__, subcls.__name__) for subcls in self.__subclasses__()]
        return Enum('DataFeeds', items)

    Enum = property(get_subclasses)


class DataFeed(metaclass=DataFeedMetaClass):
    # TODO: We will have another module that calls this function asynchronously every few 
    #  seconds / minutes (to avoid quota). Every DataFeed will run in its own subprocess / container.
    @abstractmethod
    async def generate_latest_bodies(self, 
        searchterm: str='', 
        start: datetime=None, 
        end: datetime=None,  
        limit: int=FETCH_LIMIT, 
    ):
        raise NotImplementedError()