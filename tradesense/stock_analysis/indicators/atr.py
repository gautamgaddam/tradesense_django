import pandas as pd
import numpy as np

def calculate(data, window=14):
    df = pd.DataFrame(data)
    df['high-low'] = df['high'] - df['low']
    df['high-pc'] = abs(df['high'] - df['close'].shift(1))
    df['low-pc'] = abs(df['low'] - df['close'].shift(1))

    df['tr'] = df[['high-low', 'high-pc', 'low-pc']].max(axis=1)
    atr = df['tr'].rolling(window=window).mean()

    atr = np.where(np.isnan(atr), 0, atr)  # Replace NaN values with 0

    trend_signal = "volatile" if atr[-1] > atr[-2] else "stable"

    return {"value": round(atr[-1], 5), "signal": trend_signal} if len(atr) > 0 else None
