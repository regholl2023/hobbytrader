from hobbytrader import yahoo

def test_yahoo_daily_prices_single_symbol():
    # Test for bad symbols parameter
    single_symbol = 'TSLA'
    data = yahoo.daily_prices(single_symbol)
    assert data is None

def test_yahoo_daily_prices_single_symbol_in_list():
    # Test for bad symbols parameter
    single_symbol = ['TSLA']
    data = yahoo.daily_prices(single_symbol)
    assert data is None

def test_yahoo_daily_prices_good():
    symbols = ['TSLA', 'AAPL']
    data = yahoo.daily_prices(symbols)
    assert data is not None
    symbols_returned = data.Symbol.unique()
    assert len(symbols_returned) == len(symbols)

def test_yahoo_minute_prices_single_ticker():
    single_symbol = 'TSLA'
    data = yahoo.minute_prices(single_symbol)
    assert data is None

def test_yahoo_minute_prices_single_ticker_list():
    single_symbol = ['TSLA']
    data = yahoo.minute_prices(single_symbol)
    assert data is None

def test_yahoo_minute_prices_good():
    symbols = ['TSLA', 'AAPL']
    data = yahoo.minute_prices(symbols)
    assert data is not None
    symbols_returned = data.Symbol.unique()
    assert len(symbols_returned) == len(symbols)
    columns_returned = data.columns
    assert data.index.name == 'Datetime'
    assert 'Symbol' in columns_returned
    assert 'Open' in columns_returned
    assert 'Close' in columns_returned
    assert 'High' in columns_returned
    assert 'Low' in columns_returned
    assert 'Volume' in columns_returned

