from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Sum, OuterRef, Subquery
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django_rq import job

from hefs.classes.add_orders import AddOrders
from hefs.classes.calculate_orders import CalculateOrders
from hefs.classes.get_orders import GetOrders
from hefs.classes.pickbonnengenerator import PickbonnenGenerator
from .classes.customer_info import CustomerInfo
from .classes.financecalculator import FinanceCalculator
from .classes.veh_handler import VehHandler
from .forms import PickbonnenForm, GeneralNumbersForm
from .models import Orders, ApiUrls, AlgemeneInformatie, PickItems, Productinfo, Orderline
from .sql_commands import SqlCommands
from django.db.models import F


def index(request):
    return HttpResponse("TEST")


def show_veh(request):
    organisations_to_show = ApiUrls.objects.get(user_id=request.user.id).organisatieIDs
    veh_handler = VehHandler()
    context = veh_handler.handle_veh(organisations_to_show)
    form = GeneralNumbersForm(initial={'prognosegetal_diner': context['prognosegetal_diner'],
                                       'prognosegetal_brunch': context['prognosegetal_brunch'],
                                       'prognosegetal_gourmet': context['prognosegetal_gourmet']})
    context['form'] = form
    try:
        return render(request, 'veh.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': 'Geen orders gevonden'}
        return render(request, 'veh.html', context)

def update_general_numbers(request):
    if request.method == 'POST':
        form = GeneralNumbersForm(request.POST, request.FILES)
        if form.is_valid():
            prognosegetal_diner = form['prognosegetal_diner'].value()
            prognosegetal_brunch = form['prognosegetal_brunch'].value()
            prognosegetal_gourmet = form['prognosegetal_gourmet'].value()
            AlgemeneInformatie.objects.filter(naam='prognosegetal_diner').delete()
            AlgemeneInformatie.objects.create(naam='prognosegetal_diner', waarde=prognosegetal_diner)
            AlgemeneInformatie.objects.filter(naam='prognosegetal_brunch').delete()
            AlgemeneInformatie.objects.create(naam='prognosegetal_brunch', waarde=prognosegetal_brunch)
            AlgemeneInformatie.objects.filter(naam='prognosegetal_gourmet').delete()
            AlgemeneInformatie.objects.create(naam='prognosegetal_gourmet', waarde=prognosegetal_gourmet)
    return show_veh(request)

def show_customerinfo(request):
    userid = request.user.id
    customerinfo = CustomerInfo()
    returning_customers_overview = customerinfo.returning_customers_overview(userid)
    orders_per_date_plot = customerinfo.orders_per_date_plot(userid)
    important_numbers = customerinfo.important_numbers_table(userid)
    orders_worth_table = customerinfo.orders_worth_table(userid)
    context = {'returning_customers_overview': returning_customers_overview,
               'orders_per_date_plot': orders_per_date_plot,
               'aantal_hoofdgerechten': important_numbers[0], 'aantal_orders': important_numbers[1],
               'hoofdgerechten_per_order': important_numbers[2], 'gem_omzet_per_order': important_numbers[3],
               'customers_2020': returning_customers_overview[0], 'customers_2021': returning_customers_overview[1],
               'customers_2022': returning_customers_overview[2], 'returning_customers_2021': returning_customers_overview[3],
               'returning_customers_2022': returning_customers_overview[4],'returning_customers_21_22': returning_customers_overview[5],
               'returning_customers_2023': returning_customers_overview[6], 'avg_orders_worth_2020': orders_worth_table[0],
               'avg_orders_worth_2021': orders_worth_table[1], 'avg_orders_worth_2022': orders_worth_table[2],
               'avg_orders_worth_2023': orders_worth_table[3]}
    try:
        return render(request, 'customerinfo.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': 'Geen orders gevonden'}
        return render(request, 'customerinfo.html', context)

def show_customerlocationplot(request):
    userid = request.user.id
    customerinfo = CustomerInfo()
    customer_location_plot = customerinfo.customer_location_plot(userid)
    context = {'customer_location_plot': customer_location_plot._repr_html_()}
    try:
        return render(request, 'customerlocationplot.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': 'Geen orders gevonden'}
        return render(request, 'customerlocationplot.html', context)



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
            get_new_orders.delay(request.user.id)
            request.session['status'] = '25'
            add_orders.delay()
            request.session['status'] = '75'
            calculate_orders.delay()
            request.session['status'] = '100'
        return show_busy(request)
    else:
        if request.session['status'] == '100':
            return show_veh(request)
        return show_busy(request)


def handle_alterated_new_orders(request):
    add_orders()
    calculate_orders()
    return show_veh(request)

@job
def get_new_orders(user_id):
    print("Get new orders")
    print(user_id)
    GetOrders(user_id)


@job
def calculate_orders():
    CalculateOrders()


@job
def add_orders():
    AddOrders()


def pickbonnen_page(request):
    form = PickbonnenForm()
    context = {'form': form}
    return render(request, 'pickbonnenpage.html', context)


@job
def get_pickbonnen(request):
    if request.method == 'POST':
        form = PickbonnenForm(request.POST, request.FILES)
        if form.is_valid():
            begindatum = form['begindatum'].value()
            einddatum = form['einddatum'].value()
            conversieID = form['conversieID'].value()
            routenr = form['routenr'].value()
            PickbonnenGenerator(begindatum, einddatum, conversieID, routenr)
    response = FileResponse(open('pickbonnen.pdf', 'rb'), content_type='application/pdf', as_attachment=True)
    return response


def financial_overview_page(request):
    userid = request.user.id
    financecalculator = FinanceCalculator(userid)

    costs = financecalculator.calculate_costs()
    profit = financecalculator.calculate_profit(userid)

    context = {'percentual_costs_table': costs[0], 'fixed_costs': costs[1],
               'variable_costs': costs[2], 'percentual_costs': costs[3], 'percentual_costs_incl_btw': costs[4],
               'total_fixed_costs': costs[5], 'fixed_costs_incl_btw': costs[6], 'total_variable_costs': costs[7],
               'total_variable_costs_incl_btw': costs[8], 'total_costs': costs[9], 'total_costs_incl_btw': costs[10],
               'totale_inkomsten': profit[0], 'inkomsten_zonder_verzendkosten': profit[1],
               'aantal_hoofdgerechten': profit[2], 'aantal_orders': profit[3]
               }
    try:
        return render(request, 'financialoverviewpage.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': 'Geen orders gevonden'}
        return render(request, 'financialoverviewpage.html', context)
