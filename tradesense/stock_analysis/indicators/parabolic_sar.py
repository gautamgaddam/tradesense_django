import pandas as pd
import numpy as np
from decimal import Decimal

def calculate(data, af_start=0.02, af_increment=0.02, af_max=0.2):
    df = pd.DataFrame(data)

    psar = df['close'].copy()
    uptrend = True
    af = af_start
    ep = df['low'][0]
    sar = df['high'][0]

    for i in range(1, len(df)):
        prev_psar = psar[i - 1]
        prev_ep = ep
        prev_sar = sar
        curr_high = df['high'][i]
        curr_low = df['low'][i]

        if uptrend:
            sar = prev_sar + af * (prev_ep - prev_sar)
            if curr_low < sar:
                uptrend = False
                if i >= 2:
                    sar = max(df['high'][i - 1], df['high'][i - 2])
                else:
                    sar = df['high'][i - 1]
                af = af_start
                ep = curr_low
            else:
                ep = max(ep, curr_high)
                if ep > prev_ep:
                    af = min(af_max, af + af_increment)
        else:
            sar = prev_sar - af * (prev_sar - prev_ep)
            if curr_high > sar:
                uptrend = True
                if i >= 2:
                    sar = min(df['low'][i - 1], df['low'][i - 2])
                else:
                    sar = df['low'][i - 1]
                af = af_start
                ep = curr_high
            else:
                ep = min(ep, curr_low)
                if ep < prev_ep:
                    af = min(af_max, af + af_increment)

        psar[i] = sar

    # Replace NaN values with 0
    psar = np.where(np.isnan(psar), 0, psar)

    final_value = float(round(psar[-1], 5))
    signal = "bullish" if uptrend else "bearish"

    return {"value": Decimal(final_value), "signal": signal} if len(psar) > 0 else None
