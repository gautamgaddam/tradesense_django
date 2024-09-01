from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., 'India'
    code = models.CharField(max_length=10, unique=True)  # e.g., 'IN'

    def __str__(self):
        return f"{self.name} ({self.code})"

class Market(models.Model):
    name = models.CharField(max_length=100)  # e.g., 'NSE', 'BSE'
    country = models.ForeignKey(Country, related_name='markets', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.country.name}"

class Exchange(models.Model):
    name = models.CharField(max_length=100)  # e.g., 'National Stock Exchange'
    market = models.ForeignKey(Market, related_name='exchanges', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.market.name}"

class MarketCapCategory(models.Model):
    name = models.CharField(max_length=50)  # e.g., 'Small Cap', 'Mid Cap', 'Large Cap'

    def __str__(self):
        return self.name

class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True)  # e.g., 'RELIANCE.NS'
    name = models.CharField(max_length=255)  # e.g., 'Reliance Industries'
    exchange = models.ForeignKey(Exchange, related_name='stocks', on_delete=models.CASCADE)
    sector = models.CharField(max_length=100, null=True, blank=True)  # e.g., 'Technology'
    industry = models.CharField(max_length=100, null=True, blank=True)  # e.g., 'Technology'
    market_cap_category = models.ForeignKey(MarketCapCategory, on_delete=models.SET_NULL, null=True)
    last_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # Indicates if the stock is currently active
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('symbol', 'exchange')  # Ensure symbol is unique within an exchange

    def __str__(self):
        return f"{self.name} ({self.symbol}) - {self.exchange.name}"

class HistoricalPrice(models.Model):
    stock = models.ForeignKey(Stock, related_name='historical_prices', on_delete=models.CASCADE)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    def __str__(self):
        return f"{self.stock.symbol} on {self.date} - Close: {self.close_price}"

class DailyTechnicalIndicators(models.Model):
    stock = models.ForeignKey(Stock, related_name='technical_indicators', on_delete=models.CASCADE)
    date = models.DateField()

    # Technical indicators as JSON columns
    rsi = models.JSONField(null=True, blank=True)
    macd = models.JSONField(null=True, blank=True)
    bollinger_bands = models.JSONField(null=True, blank=True)
    sma = models.JSONField(null=True, blank=True)
    ema = models.JSONField(null=True, blank=True)
    stochastic = models.JSONField(null=True, blank=True)
    atr = models.JSONField(null=True, blank=True)
    obv = models.JSONField(null=True, blank=True)
    fibonacci_retracement = models.JSONField(null=True, blank=True)  # To store various levels of Fibonacci retracement
    ichimoku_cloud = models.JSONField(null=True, blank=True)  # To store different components of the Ichimoku Cloud
    parabolic_sar = models.JSONField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    class Meta:
        unique_together = ('stock', 'date')  # Ensure one record per stock per date

    def __str__(self):
        return f"{self.stock.symbol} - Indicators on {self.date}"