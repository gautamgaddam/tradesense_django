import pandas as pd
import yfinance as yf
from django.core.management.base import BaseCommand
from stock_analysis.models import Stock, HistoricalPrice
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Fetch daily price and update the HistoricalPrice and Stock models'

    def handle(self, *args, **kwargs):
        def fetch_and_save_daily_price(stock):
            try:
                # Fetch yesterday's date
                today = datetime.now()
                yesterday = today - timedelta(days=1)

                # Fetch the daily historical data for the stock
                ticker = yf.Ticker(stock.symbol + ".BO")
                hist_data = ticker.history(start=yesterday, end=today)

                if hist_data.empty:
                    raise ValueError(f"No historical data found for {stock.symbol}")

                last_price = None

                for date, row in hist_data.iterrows():
                    # Save to HistoricalPrice
                    HistoricalPrice.objects.create(
                        stock=stock,
                        date=date,
                        open_price=row['Open'],
                        close_price=row['Close'],
                        high_price=row['High'],
                        low_price=row['Low'],
                        volume=row['Volume'],
                    )
                    last_price = row['Close']

                # Update the stock's last_price with the closing price of the day
                if last_price is not None:
                    stock.last_price = last_price
                    stock.save(update_fields=['last_price'])

                return f"Saved daily price for {stock.symbol} and updated last_price to {last_price}"

            except Exception as e:
                return f"Error fetching daily price for {stock.symbol}: {e}"

        def update_daily_prices():
            # Fetch all stocks related to BSE exchange
            stocks = Stock.objects.filter(exchange__name="Bombay Stock Exchange")[:10]

            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_stock = {executor.submit(fetch_and_save_daily_price, stock): stock for stock in stocks}

                for future in as_completed(future_to_stock):
                    result = future.result()
                    self.stdout.write(self.style.SUCCESS(result))

        # Fetch daily prices and update the models
        update_daily_prices()
