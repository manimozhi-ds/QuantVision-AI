from tensorflow.keras.models import load_model

model = load_model("models/gru_model.keras")

import joblib

scaler = joblib.load("models/gru_scaler.pkl")


def predict_market(df):

    latest = df[[
        "RSI",
        "MACD",
        "MACD_SIGNAL",
        "volume"
    ]].dropna().iloc[-1:]

    prediction = model.predict(latest)[0]

    probability = model.predict_proba(latest)[0]

    confidence = round(max(probability) * 100, 2)

    if prediction == 1:
        return {
            "direction": "UP",
            "confidence": confidence
        }

    return {
        "direction": "DOWN",
        "confidence": confidence
    }