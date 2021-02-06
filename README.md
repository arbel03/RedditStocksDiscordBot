# Adaptation of wsbtickerbot

## Original purpose
wsbtickerbot is a Reddit bot, developed utilizing the Reddit PRAW API, that scrapes the entirety of r/wallstreetbets over a 24 hour period, collects all the tickers mentioned, and then performs sentiment analysis on the context. The sentiment analysis is used to classify the stocks into three categories: bullish, neutral, and bearish.

While the intention of this bot was to simply create another talking point within the subreddit, it has evolved into much more. Future plans include, but are not limited to:
- storing all collected data in a SQLite database
- utilize this data to perform simple linear regression to determine market trends from mentions and sentiment from r/wallstreetbets

## My modifications so far

I have mainly improved the parsing capabilities of the bot.

From my initial commit:

NLP Data cleaning:
    a) removed tickers that are English words
    b) filtered out tickers that are not nouns (only filtering for proper nouns removes too much such as 'AMC')
    c) filtered out some internet slang but the list that I found is not comprehensive. 
    d) obtained a more robust word list to filter “TV”, “mom”
    e) changed the predecessor’s method of cleaning to remove an words containing punctuation so web     	page extensions stop showing up as tickers
    f) remove first and last names using a module
    g) obtained a static list of tickers to check to prevent the internet slag from removing too much like 	BB and NOK.
    h) hard coded a list of slang words to not be considered.

## Note:
I have my IEX_TOKEN saved as a path variable.

In a bash terminal: export IEX_TOKEN=<YOUR_IEX_SECRET_KEY>
