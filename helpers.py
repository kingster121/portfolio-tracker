import os
import requests
import urllib.parse

from functools import wraps
from flask import request, redirect, url_for, session

import pandas as pd
from pandas_datareader import data as pdr


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={urllib.parse.quote_plus(symbol)}&outputsize=full&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "symbol": quote["Meta Data"]["2. Symbol"],
            "prices": quote["Time Series (Daily)"],
        }
    except (KeyError, TypeError, ValueError):
        return None


def get_history(tickers=[],startdate,enddate):
    """Returns dictionary of historical data for tickers"""

    # Returns data for single ticker
    def get_data(ticker):
