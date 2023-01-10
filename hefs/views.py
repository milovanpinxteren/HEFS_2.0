from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from .get_orders import GetOrders

def index(request):
    return HttpResponse("TEST")

def show_veh(request):
    return render(request, 'veh.html')

def show_customerinfo(request):
    return render(request, 'customerinfo.html')

def getorderspage(request):
    return render(request, 'getorderspage.html')

def get_orders(request):
    GetOrders(request.user.id)
    return render(request, 'getorderspage.html')

def pickbonnen_page(request):
    return render(request, 'pickbonnenpage.html')

def financial_overview_page(request):
    return render(request, 'financialoverviewpage.html')
