#Libraries

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import pandas as pd
import joblib

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from sklearn.utils.class_weight import (
    compute_class_weight
)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    GRU,
    Dense,
    Dropout,
    Bidirectional
)

from tensorflow.keras.callbacks import (
    EarlyStopping
)

from tensorflow.keras.optimizers import Adam

from ta.volatility import AverageTrueRange

from utils.api import get_stock_candles
from utils.indicators import add_indicators

#Stocks

symbols = [

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

# Load and combine data for all stocks

all_data = []

for symbol in symbols:

    print(f"\nDownloading {symbol} data...")

    try:

        df = get_stock_candles(
            symbol=symbol,
            interval="1h",
            period="180d"
        )
        df = add_indicators(df)

        df["EMA_20"] = (
            df["close"]
            .ewm(span=20)
            .mean()
        )

        df["EMA_50"] = (
            df["close"]
            .ewm(span=50)
            .mean()
        )

        df["SMA_50"] = (
            df["close"]
            .rolling(50)
            .mean()
        )

        df["RETURNS"] = (
            df["close"]
            .pct_change()
        )

        df["VOLATILITY"] = (
            df["RETURNS"]
            .rolling(10)
            .std()
        )

        df["MOMENTUM"] = (
            df["close"]
            .diff(4)
        )

        df["PRICE_RANGE"] = (
            df["high"] - df["low"]
        )

        df["RSI_MOMENTUM"] = (
            df["RSI"]
            .diff()
        )
        
        atr = AverageTrueRange(
            high=df["high"],
            low=df["low"],
            close=df["close"]
        )

        df["ATR"] = (
            atr.average_true_range()
        )

        sentiment_score = np.random.uniform(
            -1,
            1
        )

        df["SENTIMENT"] = sentiment_score

        future_return = (
            df["close"].shift(-3)
            - df["close"]
        ) / df["close"]

        df["Target"] = future_return

        df["Symbol"] = symbol

        df.dropna(inplace=True)

        all_data.append(df)

        print(f"{symbol} loaded successfully")

    except Exception as e:

        print(f"Error loading {symbol}: {e}")

df = pd.concat(
    all_data,
    ignore_index=True
)

print("\nCombined Dataset Shape:")
print(df.shape)

#Features and Target

features = [

    "close",
    "volume",

    "RSI",
    "RSI_MOMENTUM",

    "MACD",
    "MACD_SIGNAL",

    "EMA_20",
    "EMA_50",
    "SMA_50",

    "RETURNS",
    "VOLATILITY",

    "MOMENTUM",

    "PRICE_RANGE",
    
    "ATR",
    
    "SENTIMENT"
]

data = df[features].values

target = df["Target"].values

#Scale Data

scaler = MinMaxScaler()

data_scaled = scaler.fit_transform(data)

joblib.dump(
    scaler,
    "gru_scaler.pkl"
)

print("\nScaler saved")

# Create Sequences

SEQUENCE_LENGTH = 100

X = []
y = []

for i in range(
    SEQUENCE_LENGTH,
    len(data_scaled)
):

    X.append(
        data_scaled[
            i - SEQUENCE_LENGTH:i
        ]
    )

    y.append(target[i])

X = np.array(X)
y = np.array(y)

print("\nSequence Shapes:")
print("X:", X.shape)
print("y:", y.shape)

# Train/Test Split

split_index = int(len(X) * 0.8)

X_train = X[:split_index]
X_test = X[split_index:]

y_train = y[:split_index]
y_test = y[split_index:]

print("\nTrain/Test Split:")
print("X_train:", X_train.shape)
print("X_test:", X_test.shape)

# Build GRU Model

model = Sequential()

model.add(
    Bidirectional(
        GRU(
            units=64,
            return_sequences=True
        ),
        input_shape=(
            X_train.shape[1],
            X_train.shape[2]
        )
    )
)

model.add(Dropout(0.3))

model.add(
    GRU(units=32)
)

model.add(Dropout(0.3))

model.add(
    Dense(1)
)

optimizer = Adam(
    learning_rate=0.0005
)

model.compile(
    optimizer=optimizer,
    loss="huber",
    metrics=["accuracy"]
)

print("\nModel Summary:")
model.summary()

# Early Stopping

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=5,
    restore_best_weights=True
)

# Train Model

history = model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_test, y_test),
    callbacks=[early_stop]
)

# Predictions

predictions_prob = model.predict(X_test)

predictions = (
    predictions_prob > 0.45
).astype(int)

predictions = predictions.flatten()

# Evaluation Metrics

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

r2 = r2_score(
    y_test,
    predictions
)

train_loss, train_accuracy = model.evaluate(
    X_train,
    y_train,
    verbose=0
)

test_loss, test_accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=0
)

# Print Metrics

print("GRU MODEL PERFORMANCE")

print(f"MAE: {mae:.6f}")

print(f"RMSE: {rmse:.6f}")

print(f"R² Score: {r2:.4f}")

# Save Model

model.save("gru_model.keras")

print("\nGRU model saved successfully")

print("\nScaler saved successfully")