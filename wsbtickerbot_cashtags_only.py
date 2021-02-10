"""
Original code from https://github.com/RyanElliott10/wsbtickerbot
"""

import csv
import datetime
import json
import re
import sys

import operator
import pprint
import praw
import time

import util

from praw.models import MoreComments
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def final_post(subreddit, text, discussion_thread):
    """
    :subreddit (str): The subreddit to post
    :text (str): The content of the post
    :generates: post on reddit
    """

    title = str(get_date()) + discussion_thread

    print("\nPosting...")
    print(title)
    subreddit.submit(title, selftext=text)


def get_date():
    """ Returns today's date"""
    now = datetime.datetime.now()
    return now.strftime("%b %d, %Y")


def get_url(key, value, total_count):
    """
    Obtain the url and append it to a row
    :key (str): name of row headers, i.e. a stock ticker
    :value (int): count of key
    :total_count (int): proportion of total counts that key makes up
    :return: row with the fetched url included
    """
    # determine whether to use plural or singular
    mention = ("mentions", "mention")[value == 1]
    if int(value / total_count * 100) == 0:
        perc_mentions = "<1"
    else:
        perc_mentions = int(value / total_count * 100)

    # special case for $ROPE
    if key == "ROPE":
        return "${0} | [{1} {2} ({3}% of all mentions)](" \
               "https://www.homedepot.com/b/Hardware-Chains-Ropes-Rope/N-5yc1vZc2gr)".format(key, value, mention,
                                                                                             perc_mentions)
    else:
        return "${0} | [{1} {2} ({3}% of all mentions)](https://finance.yahoo.com/quote/{0}?p={0})"\
           .format(key, value, mention, perc_mentions)


def parse_section(body, tickers, ticker_dict={}):
    """ Parses the body of each comment/reply and adds to the ticker object dictionary

    :body (str): text body to use for parsing
    :tickers (list): list of valid tickers
    :ticker_dict (dict): initial dictionary of tickers
    :returns: ticker_dict(dict[Ticker]): updated with extracted tickers and their properties
    """
    found_tickers = re.findall(r'\$[A-Za-z]+', body)
    found_tickers = [ft[1:].upper() for ft in found_tickers]

    for ft in found_tickers:
        if ft in tickers:
            if ft in ticker_dict:
                ticker_dict[ft].count += 1
            else:
                ticker_dict[ft] = Ticker(ft)
                ticker_dict[ft].count = 1
            ticker_dict[ft].bodies.append(body)

    return ticker_dict


def run(mode, sub, num_submissions):
    """
    Perform pipeline:
        - Setup initial data and API connections
        - retrieve the data
        - parse data
        - output results / post to reddit
    :mode (int): flag [0 or 1] to be in production mode (0) or test mode(1)
    :sub (str): subreddit name of interest
    :num_submissions(int): number of reddit comments to obtain
    :generates: all the resulting actions of the bot
    """
    tickers_filename = "tickers.csv"
    tickers = util.read_csv_files(tickers_filename)
    ticker_dict = {}
    total_count = 0
    within24_hrs = False

    subreddit = setup(sub)
    new_posts = subreddit.new(limit=num_submissions)

    for count, post in enumerate(new_posts):
        if not post.clicked:
            ticker_dict = parse_section(post.title, tickers, ticker_dict)

            if "Daily Discussion Thread - " in post.title:
                if not within24_hrs:
                    within24_hrs = True
                else:
                    print("\nTotal posts searched: " + str(count) + "\nTotal ticker mentions: " + str(total_count))
                    break

            comments = post.comments
            for comment in comments:
                # without this, would throw AttributeError since the instance in this represents the "load more comments"
                # option
                if isinstance(comment, MoreComments):
                    continue
                ticker_dict = parse_section(comment.body, tickers, ticker_dict)

                replies = comment.replies
                for rep in replies:
                    # without this, would throw AttributeError since the instance in this represents the "load more
                    # comments" option
                    if isinstance(rep, MoreComments):
                        continue
                    ticker_dict = parse_section(rep.body, tickers, ticker_dict)

            sys.stdout.write("\rProgress: {0} / {1} posts".format(count + 1, num_submissions))
            sys.stdout.flush()

    text = "To help you YOLO your money away, here are all of the tickers mentioned at least 10 times in all the posts " \
           "within the past 24 hours (and links to their Yahoo Finance page) along with a sentiment analysis " \
           "percentage: "
    text += "\n\nTicker | Mentions | Bullish (%) | Neutral (%) | Bearish (%)\n:- | :- | :- | :- | :-"

    total_mentions = 0
    ticker_list = []

    for key in ticker_dict:
        total_mentions += ticker_dict[key].count
        ticker_list.append(ticker_dict[key])

    ticker_list = sorted(ticker_list, key=operator.attrgetter("count"), reverse=True)

    for ticker in ticker_list:
        Ticker.analyze_sentiment(ticker)

    for count, ticker in enumerate(ticker_list):
        if count == 25:
            break

        url = get_url(ticker.ticker, ticker.count, total_mentions)
        text += "\n{} | {} | {} | {}".format(url, ticker.bullish, ticker.bearish, ticker.neutral)

    text += "\n\nTake a look at my [source code](https://github.com/RyanElliott10/wsbtickerbot) and make some " \
            "contributions if you're interested. "

    if not mode:
        final_post(subreddit, text, " | Today's Top 25 WSB Tickers")

    else:
        print(
            "\nNot posting to reddit because you're in test mode\n\n*************************************************\n"
        )
        print(text)


def setup(sub):
    """
    Connects to praw api with user credentials and setups subreddit object

    :sub (str): name of subreddit
    :return subreddit (praw subreddit object): subreddit with attributes to be used downstream
    """
    if sub == "":
        sub = "wallstreetbets"

    with open("config.json") as json_data_file:
        data = json.load(json_data_file)

    reddit = praw.Reddit(client_id=data["login"]["client_id"], client_secret=data["login"]["client_secret"],
                         username=data["login"]["username"], password=data["login"]["password"],
                         user_agent=data["login"]["user_agent"])

    subreddit = reddit.subreddit(sub)

    return subreddit


class Ticker:
    def __init__(self, ticker):
        self.bearish = 0
        self.bodies = []
        self.bullish = 0
        self.count = 0
        self.neg_count = 0
        self.neutral = 0
        self.pos_count = 0
        self.sentiment = 0  # 0 is neutral
        self.ticker = ticker

    def analyze_sentiment(self):
        analyzer = SentimentIntensityAnalyzer()
        neutral_count = 0
        for text in self.bodies:
            sentiment = analyzer.polarity_scores(text)
            if (sentiment["compound"] > .005) or (sentiment["pos"] > abs(sentiment["neg"])):
                self.pos_count += 1
            elif (sentiment["compound"] < -.005) or (abs(sentiment["neg"]) > sentiment["pos"]):
                self.neg_count += 1
            else:
                neutral_count += 1

        self.bullish = int(self.pos_count / len(self.bodies) * 100)
        self.bearish = int(self.neg_count / len(self.bodies) * 100)
        self.neutral = int(neutral_count / len(self.bodies) * 100)


if __name__ == "__main__":
    # USAGE: wsbtickerbot.py [ subreddit ] [ num_submissions ]
    mode = 0
    num_submissions = 500
    sub = "wallstreetbets"

    if len(sys.argv) > 2:
        mode = 1
        sub = sys.argv[1]
        num_submissions = int(sys.argv[2])

    run(mode, sub, num_submissions)
