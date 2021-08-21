from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .types import *

from .sentiment import Sentiment
from .base import Base
from ..datafeed import DataFeed


# Represents a mention on the web of a certain ticker or tickers.
# Further processing should happen here.
class Body(Base):
    __tablename__ = 'Bodies'

    content = Column(CLOB, nullable=False)
    creation_datetime = Column(DateTime, primary_key=True)
    datafeed = Column(Enum(DataFeed.Enum), primary_key=True)
    ticker = Column(VARCHAR(6), ForeignKey('Tickers.symbol'), primary_key=True)

    # Sentiment Representation
    sentiment_positive = Column(Float)
    sentiment_negative = Column(Float)
    sentiment_compound = Column(Float)
    sentiment = composite(Sentiment,
        sentiment_positive,
        sentiment_negative,
        sentiment_compound,)
    
    def analyze_sentiment(self):
        # TODO: Maybe extract the ticker from the body before processing?
        #  Convert "I think AMC will rise!" -> "I think will rise!"
        #  maybe ML will handle the second phrase better..
        if self.sentiment:
            return self.sentiment

        # TODO: Use more analyzers such as https://deepai.org/machine-learning-model/sentiment-analysis
        #for analyzer in sentimentAnalyzers:
        #    analyzer.analyze(self.__body)
        #    analyzers_results
        result = SentimentIntensityAnalyzer().polarity_scores(self.content)
        self.sentiment = Sentiment(result["pos"], result["neg"], result["compound"])
        return self.sentiment

    # TODO: This function should return a body representation ready for insertion into our DB
    #  This should probably be moved to a different module which gathers bodies from the different datafeeds
    #  and then creates Tickers out of them, since we should slice a small section of the actual text, around the
    #  mentioning of the actual ticker. This class should not know of the Ticker concept, as it is just representing text!
    # def get_simplified_body(self):
    #     pass
