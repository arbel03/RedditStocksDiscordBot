from datetime import datetime

import asyncpraw
from .datafeed import DataFeed, FETCH_LIMIT
from ..util import read_config


class Reddit(DataFeed):
    def __init__(self, subreddit='wallstreetbets'):
        self.__subreddit = subreddit

        config = read_config()
        self.__reddit = asyncpraw.Reddit(client_id=
            config["reddit"]["client_id"], 
            client_secret=config["reddit"]["client_secret"],
            username=config["reddit"]["username"], 
            password=config["reddit"]["password"],
            user_agent=config["reddit"]["user_agent"])

    async def generate_latest_bodies(self, 
        searchterm: str='', 
        start: datetime=None, 
        end: datetime=None,  
        limit: int=FETCH_LIMIT
    ):
        from ..model import Body

        subreddit = await self.__reddit.subreddit(self.__subreddit)

        # TODO: I think we should keep posts and their title as well, and maybe even 
        #  give them more score than a regular comment as they have more exposure in reddit
        async for comment in subreddit.comments(limit=limit):
            comment_datetime = datetime.fromtimestamp(comment.created_utc)
            if (start is not None) and (comment_datetime < start):
                continue
            if (end is not None) and (comment_datetime > end):
                continue

            yield Body(content=comment.body, 
                creation_datetime=comment_datetime, 
                datafeed=DataFeed.Enum.Reddit.value)

            for reply in comment.replies:
                yield Body(content=reply.body, 
                creation_datetime=comment_datetime, 
                datafeed=DataFeed.Enum.Reddit.value)