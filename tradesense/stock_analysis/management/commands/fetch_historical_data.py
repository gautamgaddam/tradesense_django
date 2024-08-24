import pandas as pd
import yfinance as yf
from django.core.management.base import BaseCommand
from stock_analysis.models import Stock, HistoricalPrice
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Fetch historical data for the past 13 months and save it in the HistoricalPrice model'

    def handle(self, *args, **kwargs):
        def fetch_and_save_historical_data(stock):
            try:
                # Calculate the date range for the past 13 months
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30*13)
                
                # Fetch historical data for the stock
                ticker = yf.Ticker(stock.symbol + ".BO")
                hist_data = ticker.history(start=start_date, end=end_date)
                
                if hist_data.empty:
                    raise ValueError(f"No historical data found for {stock.symbol}")
                
                historical_prices = []
                for date, row in hist_data.iterrows():
                    historical_prices.append(
                        HistoricalPrice(
                            stock=stock,
                            date=date,
                            open_price=row['Open'],
                            close_price=row['Close'],
                            high_price=row['High'],
                            low_price=row['Low'],
                            volume=row['Volume'],
                        )
                    )
                
                # Bulk create historical price records
                HistoricalPrice.objects.bulk_create(historical_prices)
                return f"Saved historical data for {stock.symbol}"

            except Exception as e:
                return f"Error fetching data for {stock.symbol}: {e}"

        def update_historical_prices():
            # Fetch all stocks related to BSE exchange  
            stocks = Stock.objects.filter(exchange__name="Bombay Stock Exchange")

            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_stock = {executor.submit(fetch_and_save_historical_data, stock): stock for stock in stocks}

                for future in as_completed(future_to_stock):
                    result = future.result()
                    self.stdout.write(self.style.SUCCESS(result))

        # Update historical prices for all stocks
        update_historical_prices()
