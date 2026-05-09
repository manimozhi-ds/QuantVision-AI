import pandas as pd
import numpy as np


def backtest_strategy(df):

    """
    Backtest AI trading signals
    """

    df = df.copy()

    df["Market_Return"] = (
        df["close"]
        .pct_change()
    )

    df["Strategy_Return"] = (
        df["Signal"].shift(1)
        * df["Market_Return"]
    )

    df["Cumulative_Market"] = (
        1 + df["Market_Return"]
    ).cumprod()

    df["Cumulative_Strategy"] = (
        1 + df["Strategy_Return"]
    ).cumprod()

    sharpe_ratio = (
        np.sqrt(252)
        * (
            df["Strategy_Return"].mean()
            /
            df["Strategy_Return"].std()
        )
    )

    cumulative = df["Cumulative_Strategy"]

    rolling_max = cumulative.cummax()

    drawdown = (
        cumulative
        - rolling_max
    ) / rolling_max

    max_drawdown = drawdown.min()

    wins = (
        df["Strategy_Return"] > 0
    ).sum()

    total_trades = (
        df["Strategy_Return"] != 0
    ).sum()

    win_rate = (
        wins / total_trades
        if total_trades > 0
        else 0
    )

    total_return = (
        df["Cumulative_Strategy"]
        .iloc[-1]
        - 1
    )

    results = {

        "Total Return": total_return,

        "Sharpe Ratio": sharpe_ratio,

        "Max Drawdown": max_drawdown,

        "Win Rate": win_rate
    }

    return df, results