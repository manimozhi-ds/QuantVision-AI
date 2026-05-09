import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from streamlit_autorefresh import st_autorefresh

from utils.api import get_stock_candles
from utils.indicators import add_indicators
from utils.sentiments import get_news, analyze_news
from utils.alerts import generate_alerts
from utils.ai_engine import predict_market
from utils.backtest import backtest_strategy
from utils.signals import generate_signal

st.set_page_config(
    page_title="QuantVision AI",
    layout="wide"
)

st.markdown("""

<style>

.stApp {

    background: linear-gradient(
        135deg,
        #0f172a,
        #020617
    );
}

[data-testid="stMetric"] {

    background: rgba(
        255,
        255,
        255,
        0.05
    );

    border: 1px solid rgba(
        255,
        255,
        255,
        0.1
    );

    padding: 20px;

    border-radius: 20px;

    backdrop-filter: blur(10px);
}

h1, h2, h3 {

    color: white;
}

</style>

""", unsafe_allow_html=True)

st_autorefresh(interval=60000, key="refresh")

st.markdown("""

<h1 style='text-align: center;
color: white;
font-size: 60px;'>

QuantVision AI

</h1>

<p style='text-align: center;
font-size: 22px;
color: gray;'>

Real-Time Quantitative Market Intelligence Platform

</p>

""", unsafe_allow_html=True)

st.caption(
    "Live market updates every 60 seconds"
)

stock_options = [

    # US Stocks
    "AAPL",
    "TSLA",
    "NVDA",
    "MSFT",

    # Indian Stocks
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",

    # Indices
    "^NSEI",
    "^GSPC"
]

st.sidebar.markdown(
    "## Market Controls"
)

st.sidebar.markdown("---")

symbol = st.sidebar.selectbox(
    "Select Stock",
    stock_options
)

resolution = st.sidebar.selectbox(
    "Resolution",
    ["5m", "15m", "30m", "1h"]
)


# Fetch Data

df = get_stock_candles(
    symbol=symbol,
    interval=resolution,
    period="5d"
)

# Indicators

df = add_indicators(df)

# Tabs

tab1, tab2, tab3, tab4 = st.tabs([

    "Market",

    "AI Forecast",

    "Backtesting",

    "News"
])

# Candlestick Chart

with tab1:

    latest_close = df["close"].iloc[-1]

    previous_close = df["close"].iloc[-2]

    price_change = (
        (
            latest_close - previous_close
        )
        / previous_close
    ) * 100

    latest_rsi = (
        df["RSI"]
        .iloc[-1]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Live Price",
        f"{latest_close:.2f}"
    )

    col2.metric(
        "Daily Change",
        f"{price_change:.2f}%"
    )

    col3.metric(
        "RSI",
        f"{latest_rsi:.2f}"
    )

    fig = go.Figure(data=[go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])


    fig.update_layout(

        template="plotly_dark",

        title=f"{symbol} Price Action",

        height=700,

        font=dict(size=14),

        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),

        xaxis_rangeslider_visible=False
    )

    fig.add_trace(

        go.Scatter(

            x=df["time"],

            y=df["SMA_50"],

            name="SMA 50"
        )
    )

    fig.add_trace(

        go.Scatter(

            x=df["time"],

            y=df["EMA_50"],

            name="EMA 50"
        )
    )

    st.plotly_chart(fig, use_container_width=True)


    # RSI

    st.subheader("RSI")

    st.line_chart(
        df.set_index("time")["RSI"]
    )


    # MACD

    st.subheader("MACD")

    macd_df = df.set_index("time")[[
        "MACD",
        "MACD_SIGNAL"
    ]]

    st.line_chart(macd_df)

    # Alerts

    alerts = generate_alerts(df)

    st.subheader("Market Alerts")

    for alert in alerts:

        if "Bullish" in alert or "OVERSOLD" in alert:

            st.success(alert)

        elif "Bearish" in alert or "OVERBOUGHT" in alert:

            st.error(alert)

        else:

            st.info(alert)

# AI Prediction

with tab2:
    st.subheader("AI Prediction Engine")

    df["Predicted_Return"] = (

        (
            df["MACD"]
            - df["MACD_SIGNAL"]
        ) * 0.01

        +

        (
            (df["RSI"] - 50)
            / 1000
        )
    )

    df["Signal"] = df[
        "Predicted_Return"
    ].apply(generate_signal)

    latest_prediction = (
        df["Predicted_Return"]
        .iloc[-1]
    )

    latest_signal = (
        df["Signal"]
        .iloc[-1]
    )


    signal_text = {

        1: "BUY",

        -1: "SELL",

        0: "HOLD"
    }

    col4.metric(
        "AI Signal",
        signal_text[latest_signal]
    )

    confidence = min(
        abs(latest_prediction) * 1000,
        100
    )

    st.success(
        f"""
        Prediction: {signal_text[latest_signal]}

        Confidence: {confidence:.2f}%
        """
    )

    backtest_df, results = (
        backtest_strategy(df)
    )

with tab3:
    st.subheader("Strategy Performance")

    col1, col2 = st.columns(2)

    col3, col4 = st.columns(2)

    col1.metric(

        "Total Return",

        f"{results['Total Return']:.2%}"
    )

    col2.metric(

        "Sharpe Ratio",

        f"{results['Sharpe Ratio']:.2f}"
    )

    col3.metric(

        "Max Drawdown",

        f"{results['Max Drawdown']:.2%}"
    )

    col4.metric(

        "Win Rate",

        f"{results['Win Rate']:.2%}"
    )

    st.subheader("Strategy Equity Curve")

    fig2 = go.Figure()

    fig2.add_trace(

        go.Scatter(

            x=backtest_df["time"],

            y=backtest_df[
                "Cumulative_Market"
            ],

            name="Market"
        )
    )

    fig2.add_trace(

        go.Scatter(

            x=backtest_df["time"],

            y=backtest_df[
                "Cumulative_Strategy"
            ],

            name="AI Strategy"
        )
    )

    fig2.update_layout(

        height=500,

        template="plotly_dark",

        title="AI Strategy vs Market"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# News Sentiment
with tab4:
    st.subheader("News Sentiment Analysis")

    query = symbol.replace(".NS", "")

    news = get_news(query)

    sentiment_df = analyze_news(news)

    st.dataframe(sentiment_df)