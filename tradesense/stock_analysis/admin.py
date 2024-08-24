from django.contrib import admin
from .models import Country, Market, Exchange, Stock, HistoricalPrice, MarketCapCategory

# Admin for Country
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name',)

admin.site.register(Country, CountryAdmin)

# Admin for Market
class MarketAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')

admin.site.register(Market, MarketAdmin)

# Admin for Exchange
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('name', 'market')
    list_filter = ('market',)
    search_fields = ('name', 'market__name')

admin.site.register(Exchange, ExchangeAdmin)

# Admin for MarketCapCategory
class MarketCapCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(MarketCapCategory, MarketCapCategoryAdmin)

# Admin for Stock
class StockAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'exchange', 'sector', 'market_cap_category', 'last_price', 'is_active', 'updated_at')
    search_fields = ('symbol', 'name')
    list_filter = ('exchange', 'sector', 'market_cap_category', 'is_active')

admin.site.register(Stock, StockAdmin)

# Admin for HistoricalPrice
class HistoricalPriceAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'open_price', 'close_price', 'high_price', 'low_price', 'volume')
    search_fields = ('stock__symbol',)
    list_filter = ('date', 'stock__exchange')

admin.site.register(HistoricalPrice, HistoricalPriceAdmin)
