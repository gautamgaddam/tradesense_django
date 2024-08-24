from django.core.management.base import BaseCommand
import yfinance as yf
from stock_analysis.models import Stock, HistoricalPrice

class Command(BaseCommand):
    help = 'Fetches stock data from NSE and BSE and saves it to the database'

    def handle(self, *args, **kwargs):
        indian_stocks = {
            'RELIANCE.NS': {'name': 'Reliance Industries', 'exchange': 'NSE'},
            'TCS.NS': {'name': 'Tata Consultancy Services', 'exchange': 'NSE'},
            'INFY.NS': {'name': 'Infosys', 'exchange': 'NSE'},
        }

        for symbol, details in indian_stocks.items():
            # Save stock data
            stock = self.save_stock(symbol, details['name'], details['exchange'])

            # Fetch historical data
            data = self.fetch_stock_data(symbol)

            # Save historical data
            self.save_historical_data(stock, data)

    def save_stock(self, symbol, name, exchange):
        stock, created = Stock.objects.get_or_create(
            symbol=symbol,
            defaults={'name': name, 'exchange': exchange}
        )
        if not created:
            stock.name = name
            stock.exchange = exchange
            stock.save()
        return stock

    def fetch_stock_data(self, ticker, start_date='2023-01-01', end_date='2024-01-01'):
        return yf.download(ticker, start=start_date, end=end_date)

    def save_historical_data(self, stock, historical_data):
        for index, row in historical_data.iterrows():
            HistoricalPrice.objects.create(
                stock=stock,
                date=index,
                open_price=row['Open'],
                close_price=row['Close'],
                high_price=row['High'],
                low_price=row['Low'],
                volume=row['Volume']
            )
        self.stdout.write(self.style.SUCCESS(f'Successfully saved historical data for {stock.symbol}'))
