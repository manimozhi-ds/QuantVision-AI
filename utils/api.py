import yfinance as yf
import requests
import pandas as pd
import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")

BASE_URL = "https://finnhub.io/api/v1"


def get_stock_candles(
    symbol="RELIANCE.NS",
    interval="5m",
    period="5d"
):

    df = yf.download(
        tickers=symbol,
        interval=interval,
        period=period,
        auto_adjust=True
    )

    df.reset_index(inplace=True)

    df.columns = [
        "time",
        "close",
        "high",
        "low",
        "open",
        "volume"
    ]

    return df


def get_company_news(symbol="RELIANCE"):

    today = pd.Timestamp.today()
    last_week = today - pd.Timedelta(days=7)

    url = f"{BASE_URL}/company-news"

    params = {
        "symbol": symbol,
        "from": last_week.strftime("%Y-%m-%d"),
        "to": today.strftime("%Y-%m-%d"),
        "token": API_KEY
    }

    response = requests.get(url, params=params)

    return response.json()