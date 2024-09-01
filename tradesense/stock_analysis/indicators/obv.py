import pandas as pd
import numpy as np

def calculate(data):
    df = pd.DataFrame(data)
    df['direction'] = df['close'].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    df['obv'] = (df['volume'] * df['direction']).cumsum()

    # Replace NaN values with 0
    df['obv'] = np.where(np.isnan(df['obv']), 0, df['obv'])

    signal = None
    if df['obv'].iloc[-1] > df['obv'].iloc[-2]:
        signal = "bullish"
    elif df['obv'].iloc[-1] < df['obv'].iloc[-2]:
        signal = "bearish"
    else:
        signal = "neutral"

    return {"value": int(df['obv'].iloc[-1]), "signal": signal} if len(df['obv']) > 0 else None
