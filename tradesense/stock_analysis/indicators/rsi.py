import pandas as pd

def calculate(data, period=14):
    """
    The calculate function computes the Relative Strength Index (RSI) for a given
    stock’s closing prices over a specified period (default 14 days). RSI is a 
    momentum oscillator that helps identify overbought or oversold conditions 
    in the stock’s price, making it a useful tool for traders and investors.
    """
    # Convert the data into a DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Calculate the price difference
    delta = df['close'].diff()
    
    # Calculate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    # Calculate the RSI
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Return the last RSI value
    return rsi.iloc[-1] if not rsi.empty else None
