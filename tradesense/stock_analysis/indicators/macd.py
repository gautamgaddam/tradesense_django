import pandas as pd

def calculate(data, short_window=12, long_window=26, signal_window=9):
    """
    Calculates the MACD indicator and includes a bullish/bearish signal.
    """
    df = pd.DataFrame(data)
    ema_short = df['close'].ewm(span=short_window, adjust=False).mean()
    ema_long = df['close'].ewm(span=long_window, adjust=False).mean()

    macd = ema_short - ema_long
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    histogram = macd - signal

    # Determine bullish or bearish based on MACD histogram
    trend_signal = None
    if histogram.iloc[-1] > 0:
        trend_signal = "bullish"
    elif histogram.iloc[-1] < 0:
        trend_signal = "bearish"

    return {
        'value': {'macd': round(macd.iloc[-1], 5),
        'signal': round(signal.iloc[-1], 5),
        'histogram': round(histogram.iloc[-1], 5),},
        'signal': trend_signal
    } if not df.empty else None
