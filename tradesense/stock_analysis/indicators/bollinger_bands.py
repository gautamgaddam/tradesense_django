import pandas as pd
import numpy as np

def calculate(data, window=20, window_dev=2):
    df = pd.DataFrame(data)
    sma = df['close'].rolling(window=window).mean()
    std = df['close'].rolling(window=window).std()

    upper_band = sma + (std * window_dev)
    lower_band = sma - (std * window_dev)

    sma = np.where(np.isnan(sma), 0, sma)
    upper_band = np.where(np.isnan(upper_band), 0, upper_band)
    lower_band = np.where(np.isnan(lower_band), 0, lower_band)

    trend_signal = None
    if df['close'].iloc[-1] > upper_band[-1]:
        trend_signal = "bullish"
    elif df['close'].iloc[-1] < lower_band[-1]:
        trend_signal = "bearish"

    return {
        'middle_band': round(sma[-1], 5),
        'upper_band': round(upper_band[-1], 5),
        'lower_band': round(lower_band[-1], 5),
        'signal': trend_signal
    } if len(sma) > 0 else None
