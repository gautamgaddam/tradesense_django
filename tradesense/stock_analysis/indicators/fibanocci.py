import pandas as pd
import numpy as np

def calculate(data):
    df = pd.DataFrame(data)
    max_price = df['close'].max()
    min_price = df['close'].min()
    diff = max_price - min_price

    levels = {
        'level_0': float(np.where(np.isnan(max_price), 0, round(max_price, 5))),
        'level_236': float(np.where(np.isnan(max_price - 0.236 * diff), 0, round(max_price - 0.236 * diff, 5))),
        'level_382': float(np.where(np.isnan(max_price - 0.382 * diff), 0, round(max_price - 0.382 * diff, 5))),
        'level_618': float(np.where(np.isnan(max_price - 0.618 * diff), 0, round(max_price - 0.618 * diff, 5))),
        'level_100': float(np.where(np.isnan(min_price), 0, round(min_price, 5)))
    }

    current_price = df['close'].iloc[-1]
    if current_price > levels['level_236']:
        signal = "bullish"
    elif current_price < levels['level_618']:
        signal = "bearish"
    else:
        signal = "neutral"

    return {"levels": levels, "signal": signal} if len(df) > 0 else None
