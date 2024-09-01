import pandas as pd
import numpy as np

def calculate(data, period=14):
    df = pd.DataFrame(data)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    rsi = np.where(np.isnan(rsi), 0, rsi)  # Replace NaN values with 0

    signal = None
    if rsi[-1] > 70:
        signal = "bearish"
    elif rsi[-1] < 30:
        signal = "bullish"

    return {"value": round(rsi[-1], 5), "signal": signal} if len(rsi) > 0 else None
