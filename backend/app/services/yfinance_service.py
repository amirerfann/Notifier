import yfinance as yf
from flask import current_app

def get_asset_price(ticker_symbol):
    """
    Fetches the last price for a given ticker symbol.
    Returns the price as a float or None if an error occurs.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        # Use 'regularMarketPrice' or 'currentPrice' for more up-to-date, potentially pre-market/after-hours data
        # hist = ticker.history(period="1d")
        # if not hist.empty:
        #     return round(hist['Close'].iloc[-1], 2)

        data = ticker.info
        # current_app.logger.debug(f"Yfinance data for {ticker_symbol}: {data}")

        # Prefer more specific fields if available
        price_fields = ['regularMarketPrice', 'currentPrice', 'previousClose', 'open']
        for field in price_fields:
            if field in data and data[field] is not None:
                return round(float(data[field]), 2)

        # Fallback for some commodities or indices that might use 'regularMarketPreviousClose'
        if 'regularMarketPreviousClose' in data and data['regularMarketPreviousClose'] is not None:
            return round(float(data['regularMarketPreviousClose']), 2)

        current_app.logger.warning(f"Could not find a suitable price field for {ticker_symbol} in yfinance info. Available keys: {data.keys()}")
        return None

    except Exception as e:
        current_app.logger.error(f"Error fetching price for {ticker_symbol} from yfinance: {e}")
        return None

def get_bitcoin_price():
    """Fetches the current Bitcoin (BTC-USD) price."""
    return get_asset_price("BTC-USD")

def get_gold_price():
    """Fetches the current Gold (GC=F) price."""
    return get_asset_price("GC=F")
