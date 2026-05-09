import websocket
import json
import os
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")



def on_message(ws, message):

    data = json.loads(message)

    print("\nLIVE DATA:")
    print(data)

    if data["type"] == "trade":

        trades = data["data"]

        rows = []

        for trade in trades:

            row = {
                "price": trade["p"],
                "symbol": trade["s"],
                "timestamp": trade["t"],
                "volume": trade["v"]
            }

            rows.append(row)

        df = pd.DataFrame(rows)

        df.to_csv(
            "data/live_ticks.csv",
            mode="a",
            header=False,
            index=False
        )



def on_error(ws, error):
    print("ERROR:", error)



def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")



def on_open(ws):

    print("WebSocket Connected")

    ws.send(json.dumps({
        "type": "subscribe",
        "symbol": "AAPL"
    }))

    ws.send(json.dumps({
        "type": "subscribe",
        "symbol": "TSLA"
    }))

    ws.send(json.dumps({
        "type": "subscribe",
        "symbol": "NVDA"
    }))


socket_url = f"wss://ws.finnhub.io?token={API_KEY}"

ws = websocket.WebSocketApp(
    socket_url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()