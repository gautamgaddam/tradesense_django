import pandas as pd

def calculate(data, window=20, window_dev=2):
    """
    Calculates the Bollinger Bands indicator.

    Parameters:
        data (dict): A dictionary containing at least 'date' and 'close' price lists.
        window (int): The period for the moving average. Default is 20.
        window_dev (int): The number of standard deviations for the bands. Default is 2.

    Returns:
        dict: A dictionary containing the latest values for 'middle_band', 'upper_band', and 'lower_band'.
    """
    try:
        # Convert data to pandas DataFrame
        df = pd.DataFrame(data)
        
        if df.empty or 'close' not in df:
            return None

        # Calculate the Simple Moving Average (SMA)
        sma = df['close'].rolling(window=window).mean()

        # Calculate the Standard Deviation
        std = df['close'].rolling(window=window).std()

        # Calculate Bollinger Bands
        upper_band = sma + (std * window_dev)
        lower_band = sma - (std * window_dev)

        # Get the latest values
        latest_middle_band = sma.iloc[-1]
        latest_upper_band = upper_band.iloc[-1]
        latest_lower_band = lower_band.iloc[-1]

        return {
            'middle_band': round(latest_middle_band, 5),
            'upper_band': round(latest_upper_band, 5),
            'lower_band': round(latest_lower_band, 5)
        }
    except Exception as e:
        print(f"Error calculating Bollinger Bands: {e}")
        return None
