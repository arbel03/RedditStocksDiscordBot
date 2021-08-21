import re
import csv
from datetime import datetime

from .util import *
from .model import Ticker, Body


def parse_section(
    _body: Body, 
    ticker_dict=dict(),
    use_cashtag=False, 
    ticker_list=set(),
    slang_terms=set()
):
    body = _body.content
    body = body.replace("'", "")

    if use_cashtag:
        found_tickers = re.findall(r'\$[A-Z]+', body)
        found_tickers = [ft[1:].upper() for ft in found_tickers]
    else:
        body = body.replace('$', '')
        word_list = re.sub(r"[^$\w]", " ", body).split()
        found_tickers = [w.upper() for w in word_list if w.isalnum() and len(w) > 1]

    for ft in found_tickers:
        if ft in ticker_list and ft not in slang_terms:
            if ft not in ticker_dict:
                # TODO: Add stock description / full name here
                ticker_dict[ft] = [Ticker(symbol=ft), []]
            
            _body.ticker = ft
            ticker_dict[ft][1].append(_body)


class Crawler:
    def __init__(self, datafeeds, stock_filenames, slang_filenames):
        self.__slang_terms = []
        for slang_filename in slang_filenames:
            self.__slang_terms += read_csv_files(
                get_data_file_path(slang_filename),
                delimiter='`',
                quoting=csv.QUOTE_NONE)

        self.__tickers = []
        for stock_filename in stock_filenames:
            self.__tickers += read_csv_files(get_data_file_path(stock_filename))

        self.__datafeeds = datafeeds

    async def run(self, 
        searchterm: str='', 
        start: datetime=None, 
        end: datetime=None, 
        **kwargs
    ):
        # TODO: Crawler should fetch from it's datafeeds asynchrnously
        # TODO: Enhance limits mechanism
        ticker_dict = dict()
        for datafeed in self.__datafeeds:
            async for body in datafeed.generate_latest_bodies(searchterm, start, end, **kwargs):
                parse_section(body, ticker_dict, ticker_list=self.__tickers, slang_terms=self.__slang_terms)

        return ticker_dict
