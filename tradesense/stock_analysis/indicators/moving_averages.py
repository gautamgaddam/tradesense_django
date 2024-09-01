import pandas as pd
import numpy as np

def calculate_sma(data, window=20):
    df = pd.DataFrame(data)
    sma = df['close'].rolling(window=window).mean()

    sma = np.where(np.isnan(sma), 0, sma)  # Replace NaN values with 0

    trend_signal = None
    if df['close'].iloc[-1] > sma[-1]:
        trend_signal = "bullish"
    elif df['close'].iloc[-1] < sma[-1]:
        trend_signal = "bearish"

    return {"value": round(sma[-1], 5), "signal": trend_signal} if len(sma) > 0 else {"value": None}

def calculate_ema(data, window=20):
    df = pd.DataFrame(data)
    ema = df['close'].ewm(span=window, adjust=False).mean()

    ema = np.where(np.isnan(ema), 0, ema)  # Replace NaN values with 0

    trend_signal = None
    if df['close'].iloc[-1] > ema[-1]:
        trend_signal = "bullish"
    elif df['close'].iloc[-1] < ema[-1]:
        trend_signal = "bearish"

    return {"value": round(ema[-1], 5), "signal": trend_signal} if len(ema) > 0 else {"value": None}