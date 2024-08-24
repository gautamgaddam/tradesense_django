import pandas as pd
import yfinance as yf
from django.core.management.base import BaseCommand
from stock_analysis.models import Country, Market, Exchange, Stock
import os
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
class Command(BaseCommand):
    help = 'Migrate stock data from CSV files into the database'

    def handle(self, *args, **kwargs):
        # Load CSV data into pandas DataFrames
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bse_file_path = os.path.join(base_dir, 'data', 'BSE.csv')
        bse_data = pd.read_csv(bse_file_path)


        def migrate_data():
            # Define the country
            country, _ = Country.objects.get_or_create(name="India", code="IN")

            # Process BSE data
            for index, row in bse_data.iterrows():
                market, _ = Market.objects.get_or_create(name="BSE", country=country)
                exchange, _ = Exchange.objects.get_or_create(name="Bombay Stock Exchange", market=market)
                # market_cap_category, _ = MarketCapCategory.objects.get_or_create(name=row['market_cap_category'])
                
                stock, created = Stock.objects.update_or_create(
                    symbol=row['Symbol'],
                    exchange=exchange,
                    defaults={
                        'name': row['Name'],
                        'sector': row.get('Sector', None),
                        'last_price': None,
                        'is_active': True,
                        'industry': row.get("Industry", None),
                        'market_cap_category': None,
                    }
                )
                if created:
                    print(f"Created stock {stock.symbol}")
                else:
                    print(f"Updated stock {stock.symbol}")

            # Process NSE data similarly
            # for index, row in nse_data.iterrows():
            #     market, _ = Market.objects.get_or_create(name="NSE", country=country)
            #     exchange, _ = Exchange.objects.get_or_create(name="National Stock Exchange", market=market)
            #     market_cap_category, _ = MarketCapCategory.objects.get_or_create(name=row['market_cap_category'])

            #     stock, created = Stock.objects.update_or_create(
            #         symbol=row['symbol'],
            #         exchange=exchange,
            #         defaults={
            #             'name': row['name'],
            #             'sector': row.get('sector', None),
            #             'last_price': row.get('last_price', None),
            #             'is_active': True,
            #             'market_cap_category': market_cap_category,
            #         }
            #     )
            #     if created:
            #         print(f"Created stock {stock.symbol}")
            #     else:
            #         print(f"Updated stock {stock.symbol}")

        
        
        def fetch_stock_data(stock):
            try:
                ticker = yf.Ticker(stock.symbol + ".BO")
                stock_info = ticker.info
                # print("ticker" , ticker.info)
                # Fetch last price
                last_price = stock_info.get('previousClose')
                if last_price is None:
                    raise ValueError("Missing 'previousClose' in stock info")

                # Fetch market cap
                market_cap = stock_info.get('marketCap')
                if market_cap is None:
                    raise ValueError("Missing 'marketCap' in stock info")

                # Determine market cap category
                if market_cap < 2e9:  # Less than 2 billion USD
                    category_id = 3  # Small Cap
                elif 2e9 <= market_cap < 10e9:  # Between 2 billion and 10 billion USD
                    category_id = 2  # Mid Cap
                else:  # Greater than or equal to 10 billion USD
                    category_id = 1  # Large Cap

                return {
                    'stock': stock,
                    'last_price': last_price,
                    'market_cap_category_id': category_id
                }

            except Exception as e:
                return {
                    'stock': stock,
                    'error': str(e)
                }

        def update_stock_prices_and_market_cap():
            failed_updates = []  # List to collect symbols that failed to update
            stocks_to_update = []

            # Fetch all stocks related to BSE exchange
            stocks = Stock.objects.filter(exchange__name="Bombay Stock Exchange")
            print("fetching stoc close price for stocks", stocks.__len__)
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_stock = {executor.submit(fetch_stock_data, stock): stock for stock in stocks}

                for future in as_completed(future_to_stock):
                    result = future.result()

                    if 'error' in result:
                        self.stderr.write(self.style.ERROR(f"Error updating {result['stock'].symbol}: {result['error']}"))
                        failed_updates.append({
                            "symbol": result['stock'].symbol,
                            "error": result['error']
                        })
                    else:
                        stock = result['stock']
                        stock.last_price = result['last_price']
                        stock.market_cap_category_id = result['market_cap_category_id']
                        stocks_to_update.append(stock)

                        self.stdout.write(self.style.SUCCESS(
                            f"Prepared {stock.symbol} for update: last_price={result['last_price']}, "
                            f"market_cap_category_id={result['market_cap_category_id']}"
                        ))

            # Perform bulk update
            if stocks_to_update:
                Stock.objects.bulk_update(stocks_to_update, ['last_price', 'market_cap_category_id'])
                self.stdout.write(self.style.SUCCESS(f"Bulk updated {len(stocks_to_update)} stocks."))

            # Save failed updates to CSV
            if failed_updates:
                failed_folder_path = os.path.join(base_dir, 'management', 'failed_updates')
                os.makedirs(failed_folder_path, exist_ok=True)  # Create the folder if it doesn't exist
                
                # Add timestamp to the filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                failed_csv_filename = f'failed_last_price_market_cap_{timestamp}.csv'
                failed_csv_path = os.path.join(failed_folder_path, failed_csv_filename)
                
                failed_df = pd.DataFrame(failed_updates)
                failed_df.to_csv(failed_csv_path, index=False)
                self.stdout.write(self.style.WARNING(f"Failed updates saved to {failed_csv_path}"))
            else:
                self.stdout.write(self.style.SUCCESS("All stocks updated successfully."))

        # Run the migration
        # migrate_data()

        # Update prices and market cap categories
        # update_stock_prices_and_market_cap()