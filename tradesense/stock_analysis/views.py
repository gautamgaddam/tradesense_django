from django.shortcuts import render
from .models import Stock
# Create your views here.



def stock_list(request):
    stocks = Stock.objects.all()
    return render(request, 'stock_analysis/stock_list.html', {'stocks': stocks})
