import pandas as pd

def calculate(data, short_window=12, long_window=26, signal_window=9):
    """
    Calculates the MACD (Moving Average Convergence Divergence) indicator.

    Parameters:
        data (dict): A dictionary containing at least 'date' and 'close' price lists.
        short_window (int): The period for the short-term EMA. Default is 12.
        long_window (int): The period for the long-term EMA. Default is 26.
        signal_window (int): The period for the signal line EMA. Default is 9.

    Returns:
        dict: A dictionary containing the latest values for 'macd', 'signal', and 'histogram'.
    """
    try:
        # Convert data to pandas DataFrame
        df = pd.DataFrame(data)
        
        if df.empty or 'close' not in df:
            return None

        # Calculate EMAs
        ema_short = df['close'].ewm(span=short_window, adjust=False).mean()
        ema_long = df['close'].ewm(span=long_window, adjust=False).mean()

        # Calculate MACD and Signal Line
        macd = ema_short - ema_long
        signal = macd.ewm(span=signal_window, adjust=False).mean()

        # Calculate MACD Histogram
        histogram = macd - signal

        # Get the latest values
        latest_macd = macd.iloc[-1]
        latest_signal = signal.iloc[-1]
        latest_histogram = histogram.iloc[-1]

        return {
            'macd': round(latest_macd, 5),
            'signal': round(latest_signal, 5),
            'histogram': round(latest_histogram, 5)
        }
    except Exception as e:
        print(f"Error calculating MACD: {e}")
        return None
