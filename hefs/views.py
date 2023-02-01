import requests
from django.db.models import Sum
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from hefs.classes.add_orders import AddOrders
from hefs.classes.calculate_orders import CalculateOrders
from .forms import PickbonnenForm
from hefs.classes.get_orders import GetOrders
from .models import PickItems, Orders, ApiUrls, PercentueleKosten, VasteKosten, VariableKosten, AlgemeneInformatie
from hefs.classes.pickbonnengenerator import PickbonnenGenerator
from django.db import connection
from .sql_commands import SqlCommands



def index(request):
    return HttpResponse("TEST")


def show_veh(request):
    organisations_to_show = ApiUrls.objects.get(user_id=request.user.id).organisatieIDs
    prognosegetal = AlgemeneInformatie.objects.get(naam='prognosegetal').waarde
    aantal_hoofdgerechten = AlgemeneInformatie.objects.get(naam='aantalHoofdgerechten').waarde
    aantal_orders = AlgemeneInformatie.objects.get(naam='aantalOrders').waarde
    prognosefractie = prognosegetal / aantal_hoofdgerechten
    dates = Orders.objects.filter(organisatieID__in=organisations_to_show).order_by('afleverdatum').values_list('afleverdatum').distinct()
    if not dates:
        context = {'table': '', 'column_headers': '', 'veh_is_empty': 'Geen producten gevonden, weet u zeker dat u met de juiste account bent ingelogd?'}
    else:
        date_array = []
        for date in dates:
            date_array.append(date)
        cursor = connection.cursor()
        sql_veh = SqlCommands().get_veh_command(date_array, prognosefractie)
        cursor.execute(sql_veh)
        veh = cursor.fetchall()
        context = {'table': veh, 'column_headers': date_array, 'prognosegetal': prognosegetal,
                   'aantal_hoofdgerechten': aantal_hoofdgerechten, 'aantal_orders': aantal_orders}
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

# @job
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
    percentual_costs = PercentueleKosten.objects.all()
    fixed_costs = VasteKosten.objects.all()
    variable_costs = VariableKosten.objects.all()
    organisations_to_show = ApiUrls.objects.get(user_id=request.user.id).organisatieIDs
    totale_inkomsten = Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(Sum('orderprijs')).get('orderprijs__sum')
    totale_verzendkosten = Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(Sum('verzendkosten')).get('verzendkosten__sum')
    inkomsten_zonder_verzendkosten = totale_inkomsten - totale_verzendkosten
    context = {'percentual_costs': percentual_costs, 'fixed_costs': fixed_costs,
               'variable_costs': variable_costs, 'totale_inkomsten': totale_inkomsten,
               'inkomsten_zonder_verzendkosten': inkomsten_zonder_verzendkosten}
    return render(request, 'financialoverviewpage.html', context)
