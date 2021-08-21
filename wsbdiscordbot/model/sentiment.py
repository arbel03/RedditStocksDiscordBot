from __future__ import annotations


class Sentiment(object):
    def __init__(self, positive=0, negative=0, compound=0):
        self.positive = positive
        self.negative = negative
        self.compound = compound

    def __composite_values__(self):
        return self.positive, self.negative, self.compound

    def __repr__(self):
        return "{}(positive={:.02f}, negative={:.02f}, compound={:.02f})".format(
            self.__name__, self.positive, self.negative, self.compound)

    def __eq__(self, other):
        return isinstance(other, Sentiment) and \
            other.compound == self.compound and \
            other.positive == self.positive and \
            other.negative == self.negative

    def __ne__(self, other):
        return not self.__eq__(other)
