"""
Original code from https://github.com/RyanElliott10/wsbtickerbot
"""

import csv
import datetime
import json
import re
import sys

import nltk
import operator
import pprint
import praw
import time

from iexfinance.stocks import Stock as IEXStock
from names_dataset import NameDataset
from nltk.corpus import words, wordnet
from praw.models import MoreComments
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def extract_ticker(body, start_index):
    """
   Given a starting index and text, this will extract the ticker, return None if it is incorrectly formatted.

   Inputs:
       body (str): sentence / paragraph of text
       start_index (int):

   Returns:
       ticker (str): the extracted ticker
   """
    count = 0
    ticker = ""

    for char in body[start_index:]:
        # if it should return
        if not char.isalpha():
            # if there aren't any letters following the $
            if count == 0:
                return None

            return ticker.upper()
        else:
            ticker += char
            count += 1

    ticker = ticker.upper()

    return ticker


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


def parse_section(body, names, slang_terms, tickers, ticker_dict={}):
    """ Parses the body of each comment/reply and adds to the ticker object dictionary

    :body (str): text body to use for parsing
    :names (NameDataset): names from names dataset
    :slang_terms (list): list of internet slang words
    :tickers (list): list of valid tickers
    :ticker_dict (dict): initial dictionary of tickers
    :returns: ticker_dict(dict[Ticker]): updated with extracted tickers and their properties
    """

    blacklist_words = [
        "YOLO", "TOS", "CEO", "CFO", "CTO", "DD", "BTFD", "WSB", "OK", "RH",
        "KYS", "FD", "TYS", "US", "USA", "IT", "ATH", "RIP", "BMW", "GDP",
        "OTM", "ATM", "ITM", "IMO", "LOL", "DOJ", "BE", "PR", "PC", "ICE",
        "TYS", "ISIS", "PRAY", "PT", "FBI", "SEC", "GOD", "NOT", "POS", "COD",
        "AYYMD", "FOMO", "TL;DR", "EDIT", "STILL", "LGMA", "WTF", "RAW", "PM",
        "LMAO", "LMFAO", "ROFL", "EZ", "RED", "BEZOS", "TICK", "IS", "DOW"
        "AM", "PM", "LPT", "GOAT", "FL", "CA", "IL", "PDFUA", "MACD", "HQ",
        "OP", "DJIA", "PS", "AH", "TL", "DR", "JAN", "FEB", "JUL", "AUG",
        "SEP", "SEPT", "OCT", "NOV", "DEC", "FDA", "IV", "ER", "IPO", "RISE"
        "IPA", "URL", "MILF", "BUT", "SSN", "FIFA", "USD", "CPU", "AT",
        "GG", "ELON", "HOLD", "LINE", "SUB", "MAKE", "BOT", "PPL", "BUY",
        "MOON", "APES", "GO", "WORD", "CALL", "TOUR", "LOVE", "STAY",
        "HAHA", "ALOT", "COM", "GOV", "ORG", "TF", "MONKE"
    ]

    blacklist_words.extend(list(set(slang_terms).difference(set(tickers))))

    if '$' in body:
        index = body.find('$') + 1
        word = extract_ticker(body, index)

        if word and word not in blacklist_words:
            try:
                # special case for $ROPE
                if word != "ROPE":
                    price = IEXStock(word).get_price()
                    if word in ticker_dict:
                        ticker_dict[word].count += 1
                        ticker_dict[word].bodies.append(body)
                    else:
                        ticker_dict[word] = Ticker(word)
                        ticker_dict[word].count = 1
                        ticker_dict[word].bodies.append(body)
            except Exception as e:
                print("exception in adding %s to dictionary", word)
                print(e)
                pass

    words_ = body.split()
    words_ = [w for w in words_ if w.isalpha()]
    word_string = " ".join(words_)
    word_list_tokens = nltk.word_tokenize(str.lower(word_string))
    word_list_pos = nltk.pos_tag(word_list_tokens)
    word_list = [w[0].upper() for w in word_list_pos]
    word_tokens = [w[1] for w in word_list_pos]

    for count, word in enumerate(word_list):
        if word.isupper() and len(word) != 1 and (word not in blacklist_words) and len(word) <= 5 \
                and word.isalpha() and word_tokens[count] in ["NNP"] and not wordnet.synsets(word) \
                and not names.search_first_name(word) and not names.search_first_name(word):
            # sends request to IEX API to determine whether the current word is a valid ticker
            # if it isn't, it'll return an error and therefore continue on to the next word
            try:
                # special case for $ROPE
                if word != "ROPE":
                    price = IEXStock(word).get_price()
            except Exception as e:
                print("exception in updating count of %s in dictionary", word)
                print(e)
                continue

            if word in ticker_dict:
                ticker_dict[word].count += 1
            else:
                ticker_dict[word] = Ticker(word)
                ticker_dict[word].count = 1
            ticker_dict[word].bodies.append(body)

    return ticker_dict


def read_csv_files(filename, data=[], **kwargs):
    """
    :param filename (str): name of file to be read
    :param data (list): initial list, should be empty
    :param kwargs: additional formatting arguments for csv.reader
    :return: data(list) = list of parsed rows in a column
    """
    with open(filename, 'r', errors='ignore') as File:
        file_reader = csv.reader(File, **kwargs)
        for row in file_reader:
            data.append(row[0])

    return data


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
    names = NameDataset()
    slang_filename = "slang_dict.doc"
    slang_terms = read_csv_files(slang_filename, delimiter='`', quoting=csv.QUOTE_NONE)
    tickers_filename = "tickers.csv"
    tickers = read_csv_files(tickers_filename)
    ticker_dict = {}
    total_count = 0
    within24_hrs = False

    subreddit = setup(sub)
    new_posts = subreddit.new(limit=num_submissions)

    for count, post in enumerate(new_posts):
        if not post.clicked:
            ticker_dict = parse_section(post.title, names, slang_terms, tickers, ticker_dict)

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
                ticker_dict = parse_section(comment.body, names, slang_terms, tickers, ticker_dict)

                replies = comment.replies
                for rep in replies:
                    # without this, would throw AttributeError since the instance in this represents the "load more
                    # comments" option
                    if isinstance(rep, MoreComments):
                        continue
                    ticker_dict = parse_section(rep.body, names, slang_terms, tickers, ticker_dict)

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
