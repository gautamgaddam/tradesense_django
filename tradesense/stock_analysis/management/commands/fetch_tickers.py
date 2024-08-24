import os
import pandas as pd
import yfinance as yf
from django.core.management.base import BaseCommand
from stock_analysis.models import Ticker

class Command(BaseCommand):
    help = 'Fetches stock tickers from NSE and BSE CSV files, categorizes them by market cap, and saves them to the database'

    def handle(self, *args, **kwargs):
        # Define the file paths relative to the project directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        nse_file_path = os.path.join(base_dir, 'data', 'NSE.csv')
        bse_file_path = os.path.join(base_dir, 'data', 'BSE.csv')

        # Load CSV files
        nse_data = pd.read_csv(nse_file_path)
        bse_data = pd.read_csv(bse_file_path)

        # Add exchange column
        nse_data['Exchange'] = 'NSE'
        bse_data['Exchange'] = 'BSE'

        # Combine NSE and BSE data
        combined_data = pd.concat([nse_data, bse_data])

        for _, row in combined_data.iterrows():
            symbol = row['Symbol']
            name = row['Name']
            exchange = row['Exchange']

            market_cap_category = self.determine_market_cap(symbol)
            self.save_ticker(symbol, name, exchange, market_cap_category)

    def determine_market_cap(self, symbol):
        # Fetch market cap from yfinance or another source
        stock_info = yf.Ticker(symbol).info
        market_cap = stock_info.get('marketCap', 0)

        if market_cap < 2e9:  # Less than 2 billion USD
            return 'small'
        elif 2e9 <= market_cap < 10e9:  # Between 2 billion and 10 billion USD
            return 'mid'
        else:
            return 'large'

    def save_ticker(self, symbol, name, exchange, market_cap_category):
        ticker, created = Ticker.objects.get_or_create(
            symbol=symbol,
            defaults={
                'name': name,
                'exchange': exchange,
                'market_cap_category': market_cap_category,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully added ticker: {symbol}'))
        else:
            self.stdout.write(self.style.WARNING(f'Ticker {symbol} already exists'))
