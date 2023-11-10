from django.contrib.auth.models import User
from django.http import HttpResponse, FileResponse, JsonResponse
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django_rq import job

from hefs.classes.add_orders import AddOrders
from hefs.classes.calculate_orders import CalculateOrders
from hefs.classes.get_orders import GetOrders
from hefs.classes.pickbonnengenerator import PickbonnenGenerator
from .classes.customer_info import CustomerInfo
from .classes.customer_location_plot import CustomerLocationPlot
from .classes.financecalculator import FinanceCalculator
from .classes.make_factuur_overview import MakeFactuurOverview
from .classes.veh_handler import VehHandler
from .forms import PickbonnenForm, GeneralNumbersForm
from .models import ApiUrls, AlgemeneInformatie, Orders
from django.contrib import messages


def index(request):
    return HttpResponse("test")


def show_veh(request):
    try:
        organisations_to_show = ApiUrls.objects.get(user_id=request.user.id).organisatieIDs
        veh_handler = VehHandler()
        context = veh_handler.handle_veh(organisations_to_show)
        form = GeneralNumbersForm(initial={'prognosegetal_diner': context['prognosegetal_diner'],
                                           'prognosegetal_brunch': context['prognosegetal_brunch'],
                                           'prognosegetal_gourmet': context['prognosegetal_gourmet']})
        context['form'] = form
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
    try:
        userid = request.user.id
        context = CustomerInfo().prepare_view(userid)
        return render(request, 'customerinfo.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': e}
        return render(request, 'customerinfo.html', context)


def show_customerlocationplot(request):
    try:
        userid = request.user.id
        customer_location_plot = CustomerLocationPlot().customer_location_plot(userid)
        context = {'customer_location_plot': customer_location_plot._repr_html_()}
        return render(request, 'customerlocationplot.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': 'Geen orders gevonden'}
        return render(request, 'customerlocationplot.html', context)


def getorderspage(request):
    return render(request, 'getorderspage.html')


def makeorderspage(request):
    numer_of_orders = Orders.objects.all().count()
    context = {'number_of_orders': numer_of_orders}
    return render(request, 'makeorderspage.html', context)


def show_busy(request):
    numer_of_orders = Orders.objects.all().count()
    status = request.session['status']
    context = {'status': status, 'number_of_orders': numer_of_orders}
    return render(request, 'waitingpage.html', context)

def update_status(request, message):
    messages.info(request, message)


def get_orders(request):
    if request.method == 'POST':
        if request.environ.get('OS', '') == "Windows_NT":
            # messages.info(request, 'Ophalen van de orders in Shopify')
            get_new_orders(request.user.id)
            # update_status(request, 'Orders opgehaald, controleren en toevoegen')
            add_orders()
            # update_status(request, 'Toegevoegd, picklijsten en VEH berekenen')
            calculate_orders()
            # update_status(request, 'Klaar met berekenen')
            request.session['status'] = '100'
        else:
            get_new_orders.delay(request.user.id)
            # update_status(request, 'Orders opgehaald, controleren en toevoegen')
            add_orders.delay()
            # update_status(request, 'Toegevoegd, picklijsten en VEH berekenen')
            calculate_orders.delay()
            # update_status(request, 'Klaar met berekenen')
            request.session['status'] = '100'
            return JsonResponse({'message': 'Klaar met berekenen'})
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
    GetOrders(user_id)


@job
def calculate_orders():
    CalculateOrders()
    return HttpResponse('Klaar met berekenen')



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
    try:
        userid = request.user.id
        financecalculator = FinanceCalculator()

        profit_table, total_ex_btw, total_incl_btw = financecalculator.calculate_profit_table(userid)
        costs_table, total_costs_ex_btw, total_costs_incl_btw, costs_of_inkoop_dict = financecalculator.calculate_costs_table(userid)
        revenue_table = financecalculator.calculate_revenue_table(total_ex_btw, total_incl_btw, total_costs_ex_btw, total_costs_incl_btw)

        table_for_prognose = profit_table.copy()
        prognose_profit_table, prognose_sum_total_ex_btw, prognose_sum_total_incl_btw = financecalculator.calculate_prognose_profit_table(table_for_prognose)
        prognose_cost_table, prognose_total_costs_ex_btw, prognose_total_costs_incl_btw = financecalculator.calculate_prognose_costs_table(costs_table)
        prognose_revenue_table = financecalculator.calculate_prognose_revenue_table(prognose_sum_total_ex_btw, prognose_sum_total_incl_btw, prognose_total_costs_ex_btw, prognose_total_costs_incl_btw)

        prognosegetal_diner = AlgemeneInformatie.objects.get(naam='prognosegetal_diner').waarde
        prognosegetal_brunch = AlgemeneInformatie.objects.get(naam='prognosegetal_brunch').waarde
        context = {
            'profit_table': profit_table, 'costs_table': costs_table, 'revenue_table': revenue_table,
            'prognose_profit_table': prognose_profit_table, 'prognose_cost_table': prognose_cost_table,
            'prognose_revenue_table': prognose_revenue_table, 'prognosegetal_diner': prognosegetal_diner,
            'prognosegetal_brunch': prognosegetal_brunch, 'costs_of_inkoop_dict': costs_of_inkoop_dict
        }
        return render(request, 'financialoverviewpage.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': e}
        return render(request, 'financialoverviewpage.html', context)


def facturen_page(request):
    make_facturen_overview = MakeFactuurOverview()
    facturen_table = make_facturen_overview.prepare_overview()
    context = {'facturen_table': facturen_table}
    return render(request, 'facturenpage.html', context)
