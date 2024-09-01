import pandas as pd
import numpy as np

def calculate(data):
    """
    Calculates Ichimoku Cloud indicator values.
    """
    df = pd.DataFrame(data)
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    high_52 = df['high'].rolling(window=52).max()
    low_52 = df['low'].rolling(window=52).min()

    df['tenkan_sen'] = (high_9 + low_9) / 2
    df['kijun_sen'] = (high_26 + low_26) / 2
    senkou_span_a = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    senkou_span_b = ((high_52 + low_52) / 2).shift(26)
    df['chikou_span'] = df['close'].shift(-26)

    # Replace NaN values with 0
    df['tenkan_sen'] = df['tenkan_sen'].fillna(0)
    df['kijun_sen'] = df['kijun_sen'].fillna(0)
    senkou_span_a = senkou_span_a.fillna(0)
    senkou_span_b = senkou_span_b.fillna(0)
    df['chikou_span'] = df['chikou_span'].fillna(0)

    current_price = df['close'].iloc[-1]
    if current_price > senkou_span_a.iloc[-1] and current_price > senkou_span_b.iloc[-1]:
        signal = "bullish"
    elif current_price < senkou_span_a.iloc[-1] and current_price < senkou_span_b.iloc[-1]:
        signal = "bearish"
    else:
        signal = "neutral"

    return {
        'tenkan_sen': float(round(df['tenkan_sen'].iloc[-1], 5)),
        'kijun_sen': float(round(df['kijun_sen'].iloc[-1], 5)),
        'senkou_span_a': float(round(senkou_span_a.iloc[-1], 5)),
        'senkou_span_b': float(round(senkou_span_b.iloc[-1], 5)),
        'chikou_span': float(round(df['chikou_span'].iloc[-1], 5)),
        'signal': signal
    } if not df['tenkan_sen'].empty else None
