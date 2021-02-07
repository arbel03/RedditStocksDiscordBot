from names_dataset import NameDataset
import unittest
import wsbtickerbot as wsb

from unittest.mock import patch


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.body = "Hey man, $NOK is cool. Not gonna waste time watching TV with my buddy bob lol. YOLO " \
                    "https://www.yahoo.com "
        self.names = NameDataset()
        self.slang_terms = ["lol"]
        self.tickers = ["NOK"]

    def test_extract_ticker(self):
        ticker = wsb.extract_ticker(self.body, 10)
        self.assertEqual("NOK", ticker)

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
        ticker_dict = wsb.parse_section(self.body, self.names, self.slang_terms, self.tickers)

        self.assertEqual("NOK", list(ticker_dict.values())[0].ticker)


if __name__ == '__main__':
    unittest.main()
