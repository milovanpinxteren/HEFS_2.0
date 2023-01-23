from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

from .add_orders import AddOrders
from .calculate_orders import CalculateOrders
from .get_orders import GetOrders

def index(request):
    return HttpResponse("TEST")

def show_veh(request):
    return render(request, 'veh.html')

def show_customerinfo(request):
    return render(request, 'customerinfo.html')

def getorderspage(request):
    return render(request, 'getorderspage.html')


def show_busy(request):
    status = request.session['status']
    context = {'status': status}
    return render(request, 'waitingpage.html', context)


def get_orders(request):
    if request.method == 'POST':
        if request.environ.get('OS', '') == "Windows_NT":
            request.session['status'] = '10'
            get_new_orders(request.user.id)
            request.session['status'] = '50'
            add_orders()
            request.session['status'] = '75'
            calculate_orders()
            request.session['status'] = '100'
        else:
            get_new_orders(request.user.id).delay()
            request.session['status'] = '25'
            add_orders()
            request.session['status'] = '75'
            calculate_orders()
            request.session['status'] = '100'
        return show_busy(request)
    else:
        if request.session['status'] == '100':
            return show_veh(request)
        return show_busy(request)

# @job
def get_new_orders(user_id):
    GetOrders(user_id)

# @job
def calculate_orders():
    CalculateOrders()

# @job
def add_orders():
    AddOrders()

def pickbonnen_page(request):
    return render(request, 'pickbonnenpage.html')

def financial_overview_page(request):
    return render(request, 'financialoverviewpage.html')
