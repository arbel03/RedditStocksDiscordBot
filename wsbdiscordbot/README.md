# Adaptation of wsbtickerbot

## Original purpose
wsbtickerbot is a Reddit bot, developed utilizing the Reddit PRAW API, that scrapes the entirety of r/wallstreetbets over a 24 hour period, collects all the tickers mentioned, and then performs sentiment analysis on the context. The sentiment analysis is used to classify the stocks into three categories: bullish, neutral, and bearish.

While the intention of this bot was to simply create another talking point within the subreddit, it has evolved into much more. Future plans include, but are not limited to:
- storing all collected data in a SQLite database
- utilize this data to perform simple linear regression to determine market trends from mentions and sentiment from r/wallstreetbets

## My modifications so far

- I have mainly improved the parsing capabilities of the bot in **wsbtickerbot.py**. I am still working on the parsing of non-cashtag tickers as it is a full-blown data science problem that cannot be solved by a table lookup or rules-based approach. It is worthwhile as 80 - 90 percent of tickers in comments do not have cashtags.

- I have a variation that only uses cashtags in **wsbtickerbot_cashtags_only.py**.

- I have another variation in **wsbtickerbot_cashtags_only_input_file.py** that takes in an input file. This approach circumvents the 24 hour limit of praw and it can analyze two months of scraped data (example in **Data Sources**) in minutes for 10 million comments. Note that the first column should contain the text content, whether it is the title of a post or a body of a comment. It's best that a dataset is filtered beforehand from an original scraped dataset to just have the text content, especially if it is very large.

## Data Sources:
- Stock tickers are from https://github.com/shilewenuw/get_all_tickers/tree/master/get_all_tickers
- 2 months of wallstreetbets datasets: https://www.kaggle.com/mattpodolak/rwallstreetbets-posts-and-comments; how to scrape similar datasets: https://www.reddit.com/r/datasets/comments/ldozc6/how_to_create_large_datasets_from_reddit/ 
