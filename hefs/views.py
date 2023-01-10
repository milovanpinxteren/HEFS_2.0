from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return HttpResponse("TEST")

def show_veh(request):
    return render(request, 'veh.html')

def show_customerinfo(request):
    return render(request, 'customerinfo.html')

def orderspage(request):
    return render(request, 'orderspage.html')

def get_orders(request):
    return render(request, 'getorderspage.html')