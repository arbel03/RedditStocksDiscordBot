from .types import *

from .base import Base


class Ticker(Base):
    __tablename__ = 'Tickers'

    symbol = Column(VARCHAR(6), primary_key=True, nullable=False)
    description = Column(VARCHAR(30))
    is_valid = Column(Boolean, default=True, nullable=False)

    # def __str__(self):
    #     # determine whether to use plural or singular
    #     mention = ("mentions", "mention")[self.count() == 1]
    #     # special case for $ROPE
    #     return "${0} [{1} {2}]".format(self.ticker, self.count(), mention)

    # def count(self):
    #     return len(self.bodies)

    # # TODO: Let the database management module decide if a Ticker is really valid.
    # #  Not database.py, it is only a database client. We need a smarter module to handle this.
    # def is_real_ticker(self):
    #     if len(self.ticker) < 2:
    #         return False
    #     ticker_string = f"${self.ticker}".lower()
    #     for body in self.bodies:
    #         if ticker_string in body.lower():
    #             return True
    #     return False

    # # This function calculates the overall sentiment for the given period
    # def analyze_sentiment(self):
    #     neutral_count = 0
    #     for body in self.bodies:
    #         if (body.get_sentiment()["compound"] > .005) or (body.get_sentiment()["pos"] > abs(body.get_sentiment()["neg"])):
    #             self.pos_count += 1
    #         elif (body.get_sentiment()["compound"] < -.005) or (abs(body.get_sentiment()["neg"]) > body.get_sentiment()["pos"]):
    #             self.neg_count += 1
    #         else:
    #             neutral_count += 1

    #     self.bullish = int(self.pos_count / len(self.bodies) * 100)
    #     self.bearish = int(self.neg_count / len(self.bodies) * 100)
    #     self.neutral = int(neutral_count / len(self.bodies) * 100)
