from .parser import parse_section


def test_parse_section():
    ticker_dict = dict()
    parse_section(
        "Hey man, $NOK is cool. So is BB. Not gonna waste time watching TV with my buddy bob lol. YOLO https://www.yahoo.com ", 
        ticker_dict=ticker_dict,
        slang_terms=["lol"], 
        ticker_list=["NOK", "BB"])

    assert set(["NOK", "BB"]) == set(ticker_dict.keys())


def test_parse_section_blacklist():
    ticker_dict = dict()
    parse_section(
        "Hey man, $NOK is cool. So is BB. Not gonna waste time watching TV with my buddy bob lol. YOLO https://www.yahoo.com ", 
        ticker_dict=ticker_dict,
        slang_terms=["BB"], 
        ticker_list=["NOK", "BB"])

    assert set(["NOK"]) == set(ticker_dict.keys())


def test_parse_section_cashtags():
    ticker_dict = dict()
    parse_section(
        "Hey man, $NOK is cool. So is BB. Not gonna waste time watching TV with my buddy bob lol. YOLO https://www.yahoo.com ", 
        ticker_dict=ticker_dict,
        use_cashtag=True,
        ticker_list=["NOK", "BB"])

    assert set(["NOK"]) == set(ticker_dict.keys())