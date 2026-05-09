import requests
import pandas as pd
import os

from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

analyzer = SentimentIntensityAnalyzer()


def get_news(query):

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY,
        "pageSize": 10
    }

    response = requests.get(url, params=params)

    return response.json()["articles"]


def analyze_news(news):

    results = []

    for article in news:

        title = article["title"]

        sentiment = analyzer.polarity_scores(title)

        results.append({
            "headline": title,
            "sentiment": sentiment["compound"]
        })

    return pd.DataFrame(results)