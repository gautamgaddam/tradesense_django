from django.core.management.base import BaseCommand
from stock_analysis.models import Stock, TechnicalIndicator, TechnicalIndicatorType, HistoricalPrice
from stock_analysis.indicators import rsi, macd, bollinger_bands
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class Command(BaseCommand):
    help = 'Calculate daily technical indicators for each stock'

    def handle(self, *args, **kwargs):
        def calculate_and_store(stock, indicator_type, value):
            TechnicalIndicator.objects.update_or_create(
                stock=stock,
                indicator_type=indicator_type,
                date=datetime.now().date(),
                defaults={'value': value}
            )

        def process_stock(stock):
            historical_prices = HistoricalPrice.objects.filter(stock=stock).order_by('date')

            if historical_prices.count() < 26:  # Ensure enough data for calculations
                return f"Not enough historical data for {stock.symbol}"

            data = {
                'date': [hp.date for hp in historical_prices],
                'close': [float(hp.close_price) for hp in historical_prices],
                'high': [float(hp.high_price) for hp in historical_prices],
                'low': [float(hp.low_price) for hp in historical_prices],
                'open': [float(hp.open_price) for hp in historical_prices],
                'volume': [hp.volume for hp in historical_prices],
            }

            # Calculate RSI
            rsi_value = rsi.calculate(data)
            if rsi_value is not None:
                calculate_and_store(stock, rsi_type, rsi_value)

            # Calculate MACD
            macd_values = macd.calculate(data)
            if macd_values is not None:
                calculate_and_store(stock, macd_type, macd_values['macd'])

            # Calculate Bollinger Bands
            bb_values = bollinger_bands.calculate(data)
            if bb_values is not None:
                calculate_and_store(stock, bb_upper_type, bb_values['upper_band'])
                calculate_and_store(stock, bb_middle_type, bb_values['sma'])  # Middle band is the SMA
                calculate_and_store(stock, bb_lower_type, bb_values['lower_band'])

            return f"Indicators for {stock.symbol} updated successfully"

        # Get all active stocks
        stocks = Stock.objects.filter(is_active=True)

        # Get or create indicator types
        global rsi_type, macd_type, bb_upper_type, bb_middle_type, bb_lower_type
        rsi_type, _ = TechnicalIndicatorType.objects.get_or_create(name='RSI')
        macd_type, _ = TechnicalIndicatorType.objects.get_or_create(name='MACD')
        bb_upper_type, _ = TechnicalIndicatorType.objects.get_or_create(name='Bollinger Bands Upper')
        bb_middle_type, _ = TechnicalIndicatorType.objects.get_or_create(name='Bollinger Bands Middle')
        bb_lower_type, _ = TechnicalIndicatorType.objects.get_or_create(name='Bollinger Bands Lower')

        # Use ThreadPoolExecutor for multithreading
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_stock, stock): stock for stock in stocks}

            for future in as_completed(futures):
                stock = futures[future]
                try:
                    result = future.result()
                    self.stdout.write(self.style.SUCCESS(result))
                except Exception as exc:
                    self.stdout.write(self.style.ERROR(f"Error processing {stock.symbol}: {exc}"))

