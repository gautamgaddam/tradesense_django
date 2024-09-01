import time  # Import the time module for measuring execution time
from decimal import Decimal
from django.core.management.base import BaseCommand
from stock_analysis.models import Stock, HistoricalPrice, DailyTechnicalIndicators
from stock_analysis.indicators import rsi, macd, bollinger_bands, moving_averages, stochastic, atr, obv, fibanocci, ichimoku, parabolic_sar
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import traceback
import numpy as np
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Calculate daily technical indicators for each stock and save bullish stocks with score'

    def handle(self, *args, **kwargs):
        all_stock_signals = []
        bulk_indicators = []

        def safe_calculate(calculate_function, data, indicator_name):
            try:
                result = calculate_function(data)
                # Convert any Decimal values to float and numpy arrays to lists
                if result:
                    for key in result:
                        if isinstance(result[key], Decimal):
                            result[key] = float(result[key])
                        elif isinstance(result[key], np.ndarray):
                            result[key] = result[key].tolist()
                return result
            except Exception as e:
                logger.error(f"Error calculating {indicator_name} for {stock.symbol}: {str(e)}")
                traceback.print_exc()
                return None

        def calculate_and_store(stock, data):
            try:
                indicators = DailyTechnicalIndicators(stock=stock, date=datetime.now().date())
                bullish_signals = 0

                # Calculate RSI
                rsi_value = safe_calculate(rsi.calculate, data, "RSI")
                if rsi_value and rsi_value.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.rsi = rsi_value

                # Calculate MACD
                macd_values = safe_calculate(macd.calculate, data, "MACD")
                if macd_values and macd_values.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.macd = macd_values

                # Calculate Bollinger Bands
                bb_values = safe_calculate(bollinger_bands.calculate, data, "Bollinger Bands")
                if bb_values and bb_values.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.bollinger_bands = bb_values

                # Calculate SMA
                sma_value = safe_calculate(moving_averages.calculate_sma, data, "SMA")
                if sma_value and sma_value.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.sma = sma_value

                # Calculate EMA
                ema_value = safe_calculate(moving_averages.calculate_ema, data, "EMA")
                if ema_value and ema_value.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.ema = ema_value

                # Calculate Stochastic Oscillator
                stochastic_values = safe_calculate(stochastic.calculate, data, "Stochastic Oscillator")
                if stochastic_values and stochastic_values.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.stochastic = stochastic_values

                # Calculate ATR
                atr_value = safe_calculate(atr.calculate, data, "ATR")
                if atr_value and atr_value.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.atr = atr_value

                # Calculate OBV
                obv_value = safe_calculate(obv.calculate, data, "OBV")
                if obv_value and obv_value.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.obv = obv_value

                # Calculate Fibonacci Retracement
                fib_levels = safe_calculate(fibanocci.calculate, data, "Fibonacci Retracement")
                if fib_levels and fib_levels.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.fibonacci_retracement = fib_levels

                # Calculate Ichimoku Cloud
                ichimoku_values = safe_calculate(ichimoku.calculate, data, "Ichimoku Cloud")
                if ichimoku_values and ichimoku_values.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.ichimoku_cloud = ichimoku_values

                # Calculate Parabolic SAR
                psar_value = safe_calculate(parabolic_sar.calculate, data, "Parabolic SAR")
                if psar_value and psar_value.get('signal') == 'bullish':
                    bullish_signals += 1
                indicators.parabolic_sar = psar_value

                if bullish_signals > 0:
                    all_stock_signals.append({
                        'stock': stock, 
                        'bullish_signals': bullish_signals, 
                        'indicators': indicators
                    })
                    return f"Indicators for {stock.symbol} updated successfully"

                return None  # Skip storing if no bullish signals

            except Exception as e:
                logger.error(f"Error processing {stock.symbol}: {str(e)}")
                traceback.print_exc()
                return f"Error processing {stock.symbol}: {str(e)}"

        def process_stock(stock):
            start_time = time.time()  # Start timer for this stock
            historical_prices = HistoricalPrice.objects.filter(stock=stock).order_by('date')

            if historical_prices.count() < 26:
                return f"No historical data or insufficient data for {stock.symbol}"

            data = {
                'date': [hp.date for hp in historical_prices],
                'close': [float(hp.close_price) for hp in historical_prices],
                'high': [float(hp.high_price) for hp in historical_prices],
                'low': [float(hp.low_price) for hp in historical_prices],
                'open': [float(hp.open_price) for hp in historical_prices],
                'volume': [hp.volume for hp in historical_prices],
            }

            result = calculate_and_store(stock, data)
            elapsed_time = time.time() - start_time  # Calculate elapsed time
            return f"{result} (Execution time: {elapsed_time:.2f} seconds)"

        # Start overall timer
        overall_start_time = time.time()

        # Get all active stocks with sufficient historical data
        stocks = Stock.objects.filter(is_active=True)

        # Use ThreadPoolExecutor for multithreading
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_stock, stock): stock for stock in stocks}

            for future in as_completed(futures):
                stock = futures[future]
                try:
                    result = future.result()
                    if result:
                        self.stdout.write(self.style.SUCCESS(result))
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"Error processing {stock.symbol}: {exc}"))

        # Rank the stocks based on the number of bullish signals
        total_stocks = len(all_stock_signals)
        if total_stocks > 0:
            ranked_stocks = sorted(all_stock_signals, key=lambda x: x['bullish_signals'], reverse=True)
            # Assign a percentile score and add it to the respective indicators
            for idx, stock_data in enumerate(ranked_stocks):
                percentile_score = 100 * (1 - (idx / total_stocks))
                stock_data['indicators'].score = round(percentile_score, 2)
                bulk_indicators.append(stock_data['indicators'])

            # Before bulk create
            for indicator in bulk_indicators:
                for key, value in indicator.__dict__.items():
                    if key != '_state':
                        try:
                            json.dumps(value)
                        except TypeError:
                            setattr(indicator, key, str(value))

            # Now perform the bulk create
            DailyTechnicalIndicators.objects.bulk_create(bulk_indicators)
            self.stdout.write(self.style.SUCCESS(f"Total bullish stocks processed and saved: {total_stocks}"))
        else:
            self.stdout.write(self.style.SUCCESS("No bullish stocks found."))

        # Print overall execution time
        overall_elapsed_time = time.time() - overall_start_time
        self.stdout.write(self.style.SUCCESS(f"Total execution time: {overall_elapsed_time:.2f} seconds"))


