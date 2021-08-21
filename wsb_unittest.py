import unittest
import wsbtickerbot as wsb

from unittest.mock import patch


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.body = "Hey man, $NOK is cool. So is BB. Not gonna waste time watching TV with my buddy bob lol. YOLO " \
                    "https://www.yahoo.com "
        self.slang_terms = ["lol"]
        self.tickers = ["NOK", "BB"]

    def test_parse_section(self):
        """
        - if it gets the cashtag
        - if it removes webpage extensions
        - if it handles the right pos filtering
        - remove blacklist words
        - remove english words
        - remove names
        - internet slang
        - keep stock tickers
        - make sure dictionary of tickers is tabulated correctly
        :return:
        """
        ticker_dict = wsb.parse_section(self.body, self.slang_terms, self.tickers)

        self.assertEqual(["NOK", "BB"], list(ticker_dict.keys()))


if __name__ == '__main__':
    unittest.main()
