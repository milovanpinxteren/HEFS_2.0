from django.conf import settings
from django.db.models import Count
from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render
from django_rq import job

from hefs.classes.add_orders import AddOrders
from hefs.classes.calculate_orders import CalculateOrders
from hefs.classes.get_orders import GetOrders
from hefs.classes.pickbonnengenerator import PickbonnenGenerator
from .classes.customer_info import CustomerInfo
from .classes.customer_location_plot import CustomerLocationPlot
from .classes.financecalculator import FinanceCalculator
from .classes.gerijptebieren.product_syncer import ProductSyncer
from .classes.gerijptebieren.products_on_original_checker import ProductsOnOriginalChecker
from .classes.gerijptebieren.products_on_partners_checker import ProductsOnPartnersChecker
from .classes.make_factuur_overview import MakeFactuurOverview
from .classes.route_copier import RouteCopier
from .classes.veh_handler import VehHandler
from hefs.classes.gerijptebieren.webhook_handler import WebhookHandler
from .forms import PickbonnenForm, GeneralNumbersForm
from .models import ApiUrls, AlgemeneInformatie, Orders, ErrorLogDataGerijptebieren
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return HttpResponse("test")

@csrf_exempt
def recieve_webhook(request):
    headers = request.headers
    body = request.body
    webhook_handler = WebhookHandler()
    webhook_handler.handle_request(headers, body)
    return HttpResponse(status=200)


def show_sync_page(request):
    error_logs = ErrorLogDataGerijptebieren.objects.all().order_by('-timestamp')
    context = {'error_logs': error_logs}
    return render(request, 'sync_page.html', context)

def start_product_sync(request):
    print('START SYNC')
    partner_websites = {'387f61-2.myshopify.com': settings.GEREIFTEBIERE_ACCESS_TOKEN}
    type = request.GET['type']
    if type == 'all_original_products':
        products_on_original_checker = ProductsOnOriginalChecker()
        all_products_list = products_on_original_checker.get_all_original_products()
        for domain_name, token in partner_websites.items():
            for product_set in all_products_list: #one product_set is 250 products
                if request.environ.get('OS', '') == "Windows_NT":
                    batch_sync_products(product_set, domain_name, token)
                else:
                    batch_sync_products(product_set, domain_name, token).delay()
    elif type == 'all_partner_products': #only 1 request per products, can be one task (unless more websites)
        products_on_partners_checker = ProductsOnPartnersChecker()
        if request.environ.get('OS', '') == "Windows_NT":
            products_on_partners_checker.check_existment_on_original()
        else:
            products_on_partners_checker.check_existment_on_original().delay()

    error_logs = ErrorLogDataGerijptebieren.objects.all().order_by('-timestamp')
    context = {'error_logs': error_logs}
    return render(request, 'sync_page.html', context)

@job
def batch_sync_products(product_set, domain_name, token):
    ProductsOnOriginalChecker().check_products_on_partner_sites(product_set, domain_name, token)  # for all products on original, checks if it exists on partner


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
        context = {'error': True, 'ErrorMessage': e}
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
        context = {'error': True, 'ErrorMessage': e}
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

def get_status(request):
    status = AlgemeneInformatie.objects.get(naam='status').waarde
    return JsonResponse({'status': status})


def get_orders(request):
    if request.method == 'POST':
        if request.environ.get('OS', '') == "Windows_NT":
            get_new_orders(request.user.id)
            add_orders()
            calculate_orders()
            request.session['status'] = '100'
        else:
            AlgemeneInformatie.objects.filter(naam='status').delete()
            AlgemeneInformatie.objects.create(naam='status', waarde=1)
            get_new_orders.delay(request.user.id)
            add_orders.delay()
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
    AlgemeneInformatie.objects.filter(naam='status').delete()
    AlgemeneInformatie.objects.create(naam='status', waarde=0)
    return render(request, 'pickbonnenpage.html', context)



def get_pickbonnen(request):
    if request.method == 'POST':
        form = PickbonnenForm(request.POST, request.FILES)
        if form.is_valid():
            begindatum = form['begindatum'].value()
            einddatum = form['einddatum'].value()
            conversieID = form['conversieID'].value()
            routenr = form['routenr'].value()
            if request.environ.get('OS', '') == "Windows_NT":
                generate_pickbonnen(begindatum, einddatum, conversieID, routenr)
            else:
                # generate_pickbonnen.delay(begindatum, einddatum, conversieID, routenr)
                PickbonnenGenerator(begindatum, einddatum, conversieID, routenr)
                response = FileResponse(open('pickbonnen.pdf', 'rb'), content_type='application/pdf',
                                        as_attachment=True)
                return response
    form = PickbonnenForm()
    context = {'form': form}
    return render(request, 'pickbonnenpage.html', context)

@job
def generate_pickbonnen(begindatum, einddatum, conversieID, routenr):
    PickbonnenGenerator(begindatum, einddatum, conversieID, routenr)

def download_pickbonnen(request):
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


def routes_page(request):
    verzendopties_counts = Orders.objects.values('verzendoptie__verzendoptie').annotate(
        count=Count('verzendoptie__verzendoptie')).order_by('-count')
    verzendopties_dict = {item['verzendoptie__verzendoptie']: item['count'] for item in verzendopties_counts}

    context = {'verzendopties_dict': verzendopties_dict}
    return render(request, 'routespage.html', context)


def copy_routes(request):
    RouteCopier().copy_routes()
    verzendopties_counts = Orders.objects.values('verzendoptie__verzendoptie').annotate(
        count=Count('verzendoptie__verzendoptie')).order_by('-count')
    verzendopties_dict = {item['verzendoptie__verzendoptie']: item['count'] for item in verzendopties_counts}

    context = {'verzendopties_dict': verzendopties_dict}
    return render(request, 'routespage.html', context)