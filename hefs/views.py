from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render

from hefs.classes.add_orders import AddOrders
from hefs.classes.calculate_orders import CalculateOrders
from .forms import PickbonnenForm
from hefs.classes.get_orders import GetOrders
from .models import PickItems, Orders
from hefs.classes.pickbonnengenerator import PickbonnenGenerator
from django.db import connection

from .sql_commands import SqlCommands


def index(request):
    return HttpResponse("TEST")


def show_veh(request):
    dates = Orders.objects.order_by('afleverdatum').values_list('afleverdatum').distinct()
    date_array = []
    for date in dates:
        date_array.append(date)
    cursor = connection.cursor()
    test = SqlCommands().get_veh_command(date_array)
    print(test)
    cursor.execute(test)
    veh = cursor.fetchall()
    print(veh)
    context = {'table': veh, 'column_headers': date_array}
    return render(request, 'veh.html', context)


def show_customerinfo(request):
    return render(request, 'customerinfo.html')


def getorderspage(request):
    return render(request, 'getorderspage.html')


def makeorderspage(request):
    return render(request, 'makeorderspage.html')


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
    form = PickbonnenForm()
    context = {'form': form}
    return render(request, 'pickbonnenpage.html', context)


def get_pickbonnen(request):
    if request.method == 'POST':
        form = PickbonnenForm(request.POST, request.FILES)
        if form.is_valid():
            begindatum = form['begindatum'].value()
            einddatum = form['einddatum'].value()
            conversieID = form['conversieID'].value()
            routenr = form['routenr'].value()
            PickbonnenGenerator(begindatum, einddatum, conversieID, routenr)
    new_form = PickbonnenForm()
    context = {'form': new_form}
    return render(request, 'pickbonnenpage.html', context)


def financial_overview_page(request):
    return render(request, 'financialoverviewpage.html')
