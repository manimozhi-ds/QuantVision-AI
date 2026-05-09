import ta


def add_indicators(df):

    df["RSI"] = ta.momentum.RSIIndicator(
        close=df["close"]
    ).rsi()

    macd = ta.trend.MACD(close=df["close"])

    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()

    df["SMA_20"] = df["close"].rolling(20).mean()
    df["SMA_50"] = (df["close"].rolling(window=50).mean())

    df["EMA_50"] = (df["close"].ewm(span=50).mean())
    
    return df