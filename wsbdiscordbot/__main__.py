import logging
import datetime
import asyncio

import discord
from terminaltables import AsciiTable

from .util import read_config, is_test_mode
from .parser import Crawler
from .database import Database
from .datafeed import *


logging.basicConfig(filename='error.log', encoding='utf-8', level=logging.ERROR)


class DiscordBot:
    def __init__(self):
        self.__database = Database.initialize(test=is_test_mode(), convert_unicode=False,
            pool_recycle=10,
            pool_size=50,
            echo=is_test_mode())
        self.__crawler = Crawler([Reddit('wallstreetbets'), Reddit('stocks')], ['nasdaq.csv', 'nyse.csv'], ['slang_dict.csv'])
        self.__client = discord.Client()
        self.__client.event(self.on_ready)
        self.__client.event(self.on_message)

    async def analyzer_task(self, ticker, bodies):
        try:
            for body in bodies:
                body.analyze_sentiment()
            self.__database.add([ticker] + bodies)
        except BaseException as ex:
            logging.exception(ex)

    async def crawler_task(self):
        start = None
        while True:
            try:
                print("Fetching...")
                tickers_dict = await self.__crawler.run(start=start, limit=100)
                print("Found tickers: {}".format(tickers_dict.keys()))
                for ticker, bodies in tickers_dict.values():
                    asyncio.create_task(self.analyzer_task(ticker, bodies))
                start = datetime.datetime.utcnow()
            except BaseException as ex:
                logging.exception(ex)
            finally:
                await asyncio.sleep(600)

    async def on_ready(self):
        print('We have logged in as {0.user}'.format(self.__client))

    async def on_message(self, message):
        if message.author == self.__client.user:
            return

        if message.content.startswith('$analyze'):
            await message.channel.send('Analyzing...')
            table = [('Ticker', 'Mentions')] + self.__database.get_ticker_mentions().limit(15).all()
            await message.channel.send(f"Displaying the top {len(table) - 1} tickers:")
            await message.channel.send(f'```{AsciiTable(table).table}```')

    def run(self, token: str, is_test: bool):
        loop = asyncio.get_event_loop()
        loop.create_task(self.crawler_task())

        if is_test:
            loop.run_forever()
            return
        
        self.__client.run(token)


def main():
    bot = DiscordBot()

    config = read_config()
    bot.run(config["discord"]["token"], is_test_mode())


if __name__ == "__main__":
    main()