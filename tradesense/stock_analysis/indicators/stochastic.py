import pandas as pd
import numpy as np

def calculate(data, period=14, k_period=3, d_period=3):
    df = pd.DataFrame(data)
    df['low_min'] = df['low'].rolling(window=period).min()
    df['high_max'] = df['high'].rolling(window=period).max()
    df['%K'] = (df['close'] - df['low_min']) / (df['high_max'] - df['low_min']) * 100
    df['%D'] = df['%K'].rolling(window=d_period).mean()

    # Replace NaN values with 0
    df['%K'] = np.where(np.isnan(df['%K']), 0, df['%K'])
    df['%D'] = np.where(np.isnan(df['%D']), 0, df['%D'])

    signal = None
    if df['%K'].iloc[-1] > df['%D'].iloc[-1]:
        signal = "bullish"
    elif df['%K'].iloc[-1] < df['%D'].iloc[-1]:
        signal = "bearish"
    else:
        signal = "neutral"

    return {
        'k_value': round(df['%K'].iloc[-1], 5),
        'd_value': round(df['%D'].iloc[-1], 5),
        'signal': signal
    } if len(df['%K']) > 0 else None
