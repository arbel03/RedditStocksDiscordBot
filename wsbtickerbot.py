import re
import sys
import praw
import time
import json
import nltk
import pprint
import operator
import datetime
import csv

from get_all_tickers import get_tickers as gt
from praw.models import MoreComments
#from iexfinance import Stock as IEXStock
from iexfinance.stocks import Stock as IEXStock
from nltk.corpus import words, wordnet
from names_dataset import NameDataset

# to add the path for Python to search for files to use my edited version of vaderSentiment
sys.path.insert(0, 'vaderSentiment/vaderSentiment')
#from vaderSentiment import SentimentIntensityAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

m = NameDataset()

slang_filename = "slang_dict.doc"

tickers = []
with open("tickers.csv",'r', errors='ignore') as tickFile:
    tickReader = csv.reader(tickFile)
    for row in tickReader:
        tickers.append(row[0])
#print(tickers)
#raise Exception("")
slang_data = []
with open(slang_filename,'r', errors='ignore') as exRtFile:
    exchReader = csv.reader(exRtFile,delimiter='`',quoting=csv.QUOTE_NONE)
    for row in exchReader:
        slang_data.append(row)

slang_terms = [row[0] for row in slang_data]
#print(slang_terms)
#raise Exception("done")
#slang_data[1] contains Acronyms
#slang_data[2] contains meaning phrases

def extract_ticker(body, start_index):
   """
   Given a starting index and text, this will extract the ticker, return None if it is incorrectly formatted.
   """
   count  = 0
   ticker = ""

   for char in body[start_index:]:
      # if it should return
      if not char.isalpha():
         # if there aren't any letters following the $
         if (count == 0):
            return None

         return ticker.upper()
      else:
         ticker += char
         count += 1

   return ticker.upper()

def parse_section(ticker_dict, body):
   """ Parses the body of each comment/reply """
   eng_words = [w.upper() for w in words.words()]
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
   blacklist_words.extend(eng_words)
   blacklist_words.extend(list(set(slang_terms).difference(set(tickers))))
   
   #print(blacklist_words)
   if '$' in body:
      #print(body)
      index = body.find('$') + 1
      word = extract_ticker(body, index)
      
      if word and word not in blacklist_words:
         #print(word)
         try:
            # special case for $ROPE
            if word != "ROPE":
               price = IEXStock(word).get_price()
               if word in ticker_dict:
                  ticker_dict[word].count += 1
                  ticker_dict[word].bodies.append(body)
               else:
                  #print("adding %s to dictionary", word)
                  ticker_dict[word] = Ticker(word)
                  ticker_dict[word].count = 1
                  ticker_dict[word].bodies.append(body)
         except Exception as e:
            #print("exception in adding %s to dictionary", word)
            #print(e)
            pass
   
   # checks for non-$ formatted comments, splits every body into list of words
   words_ = body.split()
   words_ = [w for w in words_ if w.isalpha()]
   #word_string = re.sub("[^\w]", " ",  body)
   word_string = " ".join(words_)
   word_list_tokens = nltk.word_tokenize(str.lower(word_string))
   word_list_pos = nltk.pos_tag(word_list_tokens)
   word_list = [w[0].upper() for w in word_list_pos]
   word_tokens = [w[1] for w in word_list_pos]
   for count, word in enumerate(word_list):
      # initial screening of words
      #if word == "AMC":
         #print(word_tokens[count])
      if word.isupper() and len(word) != 1 and (word.upper() not in blacklist_words) and len(word) <= 5 and word.isalpha() and word_tokens[count] in ["NNP"] and not wordnet.synsets(word) and not m.search_first_name(word) and not m.search_first_name(word):
         # sends request to IEX API to determine whether the current word is a valid ticker
         # if it isn't, it'll return an error and therefore continue on to the next word
         try:
            # special case for $ROPE
            if word != "ROPE":
               price = IEXStock(word).get_price()
         except Exception as e:
            #print("exception in updating count of %s in dictionary", word)
            #print(e)
            continue
      
         # add/adjust value of dictionary
         if word in ticker_dict:
            ticker_dict[word].count += 1
            ticker_dict[word].bodies.append(body)
         else:
            #print("updating count of %s in dictionary", word)
            ticker_dict[word] = Ticker(word)
            ticker_dict[word].count = 1
            ticker_dict[word].bodies.append(body)

   return ticker_dict

def get_url(key, value, total_count):
   # determine whether to use plural or singular
   mention = ("mentions", "mention") [value == 1]
   if int(value / total_count * 100) == 0:
         perc_mentions = "<1"
   else:
         perc_mentions = int(value / total_count * 100)
   # special case for $ROPE
   if key == "ROPE":
      return "${0} | [{1} {2} ({3}% of all mentions)](https://www.homedepot.com/b/Hardware-Chains-Ropes-Rope/N-5yc1vZc2gr)".format(key, value, mention, perc_mentions)
   else:
      return "${0} | [{1} {2} ({3}% of all mentions)](https://finance.yahoo.com/quote/{0}?p={0})".format(key, value, mention, perc_mentions)

def final_post(subreddit, text):
   # finding the daily discussino thread to post
   title = str(get_date()) + " | Today's Top 25 WSB Tickers"

   print("\nPosting...")
   print(title)
   subreddit.submit(title, selftext=text)

def get_date():
   now = datetime.datetime.now()
   return now.strftime("%b %d, %Y")

def setup(sub):
   if sub == "":
      sub = "wallstreetbets"

   with open("config.json") as json_data_file:
      data = json.load(json_data_file)

   # create a reddit instance
   reddit = praw.Reddit(client_id=data["login"]["client_id"], client_secret=data["login"]["client_secret"],
                        username=data["login"]["username"], password=data["login"]["password"],
                        user_agent=data["login"]["user_agent"])
   # create an instance of the subreddit
   subreddit = reddit.subreddit(sub)
   return subreddit


def run(mode, sub, num_submissions):
   ticker_dict = {}
   text = ""
   total_count = 0
   within24_hrs = False

   subreddit = setup(sub)
   new_posts = subreddit.new(limit=num_submissions)

   for count, post in enumerate(new_posts):
      # if we have not already viewed this post thread
      if not post.clicked:
         # parse the post's title's text
         ticker_dict = parse_section(ticker_dict, post.title)

         # to determine whether it has gone through all posts in the past 24 hours
         if "Daily Discussion Thread - " in post.title:
            if not within24_hrs:
               within24_hrs = True
            else:
               print("\nTotal posts searched: " + str(count) + "\nTotal ticker mentions: " + str(total_count))
               break
         
         # search through all comments and replies to comments
         comments = post.comments
         for comment in comments:
            # without this, would throw AttributeError since the instance in this represents the "load more comments" option
            if isinstance(comment, MoreComments):
               continue
            ticker_dict = parse_section(ticker_dict, comment.body)

            # iterate through the comment's replies
            replies = comment.replies
            for rep in replies:
               # without this, would throw AttributeError since the instance in this represents the "load more comments" option
               if isinstance(rep, MoreComments):
                  continue
               ticker_dict = parse_section(ticker_dict, rep.body)
         
         # update the progress count
         sys.stdout.write("\rProgress: {0} / {1} posts".format(count + 1, num_submissions))
         sys.stdout.flush()

   text = "To help you YOLO your money away, here are all of the tickers mentioned at least 10 times in all the posts within the past 24 hours (and links to their Yahoo Finance page) along with a sentiment analysis percentage:"
   text += "\n\nTicker | Mentions | Bullish (%) | Neutral (%) | Bearish (%)\n:- | :- | :- | :- | :-"

   total_mentions = 0
   ticker_list = []

   for key in ticker_dict:
      #print(key, ticker_dict[key].count)
      total_mentions += ticker_dict[key].count
      ticker_list.append(ticker_dict[key])

   ticker_list = sorted(ticker_list, key=operator.attrgetter("count"), reverse=True)

   for ticker in ticker_list:
      Ticker.analyze_sentiment(ticker)

   # will break as soon as it hits a ticker with fewer than 5 mentions
   for count, ticker in enumerate(ticker_list):
      if count == 25:
         break
      
      url = get_url(ticker.ticker, ticker.count, total_mentions)
      # setting up formatting for table
      text += "\n{} | {} | {} | {}".format(url, ticker.bullish, ticker.bearish, ticker.neutral)

   text += "\n\nTake a look at my [source code](https://github.com/RyanElliott10/wsbtickerbot) and make some contributions if you're interested."

   # post to the subreddit if it is in bot mode (i.e. not testing)
   if not mode:
      final_post(subreddit, text)
   # testing
   else:
      print("\nNot posting to reddit because you're in test mode\n\n*************************************************\n")
      print(text)

class Ticker:
   def __init__(self, ticker):
      self.ticker = ticker
      self.count = 0
      self.bodies = []
      self.pos_count = 0
      self.neg_count = 0
      self.bullish = 0
      self.bearish = 0
      self.neutral = 0
      self.sentiment = 0 # 0 is neutral

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

