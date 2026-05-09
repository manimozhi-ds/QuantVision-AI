def generate_alerts(df):

    alerts = []

    latest = df.iloc[-1]

    if latest["RSI"] > 70:

        alerts.append(
            "RSI indicates OVERBOUGHT conditions"
        )

    elif latest["RSI"] < 30:

        alerts.append(
            "RSI indicates OVERSOLD conditions"
        )

    else:

        alerts.append(
            "RSI in neutral zone"
        )

    if latest["MACD"] > latest["MACD_SIGNAL"]:

        alerts.append(
            "Bullish MACD crossover detected"
        )

    else:

        alerts.append(
            "Bearish MACD crossover detected"
        )

    avg_volume = (
        df["volume"]
        .rolling(20)
        .mean()
        .iloc[-1]
    )

    if latest["volume"] > avg_volume * 1.5:

        alerts.append(
            "Unusual volume activity detected"
        )

    if latest["EMA_50"] > latest["SMA_50"]:

        alerts.append(
            "Bullish trend detected"
        )

    else:

        alerts.append(
            "Bearish trend detected"
        )

    return alerts