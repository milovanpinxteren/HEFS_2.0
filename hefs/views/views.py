import datetime
from datetime import datetime, timedelta

from django.http import HttpResponse, FileResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django_rq import job

from hefs import models
from hefs.apis.paasontbijt2024transacties import Paasontbijt2024Transacties
from hefs.classes.add_orders import AddOrders
from hefs.classes.calculate_orders import CalculateOrders
from hefs.classes.customer_info import CustomerInfo
from hefs.classes.customer_location_plot import CustomerLocationPlot
from hefs.classes.financecalculator import FinanceCalculator
from hefs.classes.get_orders import GetOrders
from hefs.classes.make_factuur_overview import MakeFactuurOverview
from hefs.classes.microcash_sync.ftp_getter import FTPGetter
from hefs.classes.pickbonnengenerator import PickbonnenGenerator
from hefs.classes.routingclasses.coordinate_calculator import CoordinateCalculator
from hefs.classes.routingclasses.distance_matrix_updater import DistanceMatrixUpdater
from hefs.classes.routingclasses.route_shower import RouteShower
from hefs.classes.routingclasses.routes_generator import RoutesGenerator
from hefs.classes.shopify_sync.sync_table_updater import SyncTableUpdater
from hefs.classes.veh_handler import VehHandler
from hefs.forms import PickbonnenForm, GeneralNumbersForm
from hefs.models import ApiUrls, AlgemeneInformatie, Orders, ErrorLogDataGerijptebieren, Route, Stop, HobOrderProducts, \
    Productinfo
from hefs.views.map_views.arrival_time_calculator import ArrivalTimeCalculator
from django.db.models import Count, Q

def index(request):
    try:
        if request.user.groups.filter(name='leverancier').exists():
            organisations_to_show = ApiUrls.objects.get(user_id=request.user.id).organisatieIDs
            veh_handler = VehHandler()
            context = veh_handler.handle_veh(organisations_to_show, request.user)
            form = GeneralNumbersForm(initial={'prognosegetal_diner': context['prognosegetal_diner'],
                                               'prognosegetal_brunch': context['prognosegetal_brunch'],
                                               'prognosegetal_gourmet': context['prognosegetal_gourmet']})
            context['form'] = form
            return render(request, 'info_pages/veh.html', context)
        elif request.user.groups.filter(name='chauffeur').exists():
            route_shower = RouteShower()
            # route = Route.objects.filter(vehicle__user=request.user)
            routes = (
                Route.objects.filter(vehicle__user=request.user)
                .annotate(visited_stops=Count('stops', filter=Q(stops__visited=True)))  # Count visited stops
                .filter(visited_stops=0)  # Only include routes with no visited stops
                .order_by('date')  # Sort the queryset by date
            )
            route = routes[0]
            context = route_shower.prepare_route_showing(route)
            # return render(request, 'map.html', context)

            return render(request, 'info_pages/chauffeur_overzicht.html', context)
        elif request.user.groups.filter(name='orderpicker').exists():
            productinfo = Productinfo.objects.all()
            context = {'productinfo': productinfo}
            return render(request, 'info_pages/orderpick_page.html', context)
        return render(request, 'helpers/landingspage.html')
    except Exception as e:
        print('index exception')
        context = {'error': True, 'ErrorMessage': e}
        return render(request, 'info_pages/veh.html', context)


@csrf_exempt
def recieve_webhook(request):
    # headers = request.headers
    # body = request.body
    # webhook_handler = WebhookHandler()
    # webhook_handler.handle_request(headers, body)
    return HttpResponse(status=200)


def show_veh(request):
    try:
        organisations_to_show = ApiUrls.objects.get(user_id=request.user.id).organisatieIDs
        veh_handler = VehHandler()
        # half_product_shower = HalfProductShower()
        context = veh_handler.handle_veh(organisations_to_show, request.user)
        form = GeneralNumbersForm(initial={'prognosegetal_diner': context['prognosegetal_diner'],
                                           'prognosegetal_brunch': context['prognosegetal_brunch'],
                                           'prognosegetal_gourmet': context['prognosegetal_gourmet']})
        context['form'] = form
        # context['halfproducts'] = half_product_shower.show_half_products(context['table'])
        return render(request, 'info_pages/veh.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': e}
        return render(request, 'info_pages/veh.html', context)


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
    # try:
    userid = request.user.id
    context = CustomerInfo().prepare_view(userid)
    return render(request, 'info_pages/customerinfo.html', context)


def show_customerlocationplot(request):
    try:
        userid = request.user.id
        customer_location_plot = CustomerLocationPlot().customer_location_plot(userid)
        context = {'customer_location_plot': customer_location_plot._repr_html_()}
        return render(request, 'info_pages/customerlocationplot.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': e}
        return render(request, 'info_pages/customerlocationplot.html', context)


def getorderspage(request):
    return render(request, 'info_pages/getorderspage.html')


def makeorderspage(request):
    numer_of_orders = Orders.objects.all().count()
    context = {'number_of_orders': numer_of_orders}
    return render(request, 'info_pages/makeorderspage.html', context)


def show_busy(request):
    numer_of_orders = Orders.objects.all().count()
    status = request.session['status']
    context = {'status': status, 'number_of_orders': numer_of_orders}
    return render(request, 'helpers/waitingpage.html', context)


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
    return render(request, 'info_pages/pickbonnenpage.html', context)


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
    return render(request, 'info_pages/pickbonnenpage.html', context)


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
        costs_table, total_costs_ex_btw, total_costs_incl_btw, costs_of_inkoop_dict = financecalculator.calculate_costs_table(
            userid)
        revenue_table = financecalculator.calculate_revenue_table(total_ex_btw, total_incl_btw, total_costs_ex_btw,
                                                                  total_costs_incl_btw)

        table_for_prognose = profit_table.copy()
        prognose_profit_table, prognose_sum_total_ex_btw, prognose_sum_total_incl_btw = financecalculator.calculate_prognose_profit_table(
            table_for_prognose)
        prognose_cost_table, prognose_total_costs_ex_btw, prognose_total_costs_incl_btw = financecalculator.calculate_prognose_costs_table(
            costs_table)
        prognose_revenue_table = financecalculator.calculate_prognose_revenue_table(prognose_sum_total_ex_btw,
                                                                                    prognose_sum_total_incl_btw,
                                                                                    prognose_total_costs_ex_btw,
                                                                                    prognose_total_costs_incl_btw)

        prognosegetal_diner = AlgemeneInformatie.objects.get(naam='prognosegetal_diner').waarde
        prognosegetal_brunch = AlgemeneInformatie.objects.get(naam='prognosegetal_brunch').waarde
        context = {
            'profit_table': profit_table, 'costs_table': costs_table, 'revenue_table': revenue_table,
            'prognose_profit_table': prognose_profit_table, 'prognose_cost_table': prognose_cost_table,
            'prognose_revenue_table': prognose_revenue_table, 'prognosegetal_diner': prognosegetal_diner,
            'prognosegetal_brunch': prognosegetal_brunch, 'costs_of_inkoop_dict': costs_of_inkoop_dict
        }
        return render(request, 'info_pages/financialoverviewpage.html', context)
    except Exception as e:
        context = {'error': True, 'ErrorMessage': e}
        return render(request, 'info_pages/financialoverviewpage.html', context)


def facturen_page(request):
    make_facturen_overview = MakeFactuurOverview()
    facturen_table = make_facturen_overview.prepare_overview()
    context = {'facturen_table': facturen_table}
    return render(request, 'info_pages/facturenpage.html', context)


def routes_page(request):
    verzendopties_counts = Orders.objects.values('verzendoptie__verzendoptie').annotate(
        count=Count('verzendoptie__verzendoptie')).order_by('-count')
    verzendopties_dict = {item['verzendoptie__verzendoptie']: item['count'] for item in verzendopties_counts}

    context = {'verzendopties_dict': verzendopties_dict}
    return render(request, 'helpers/routespage.html', context)


def calculate_coordinates(request):
    calculator = CoordinateCalculator()
    calculator.calculate_coordinates()
    return render(request, 'helpers/routespage.html')


def update_distance_matrix(request):
    updater = DistanceMatrixUpdater()
    updater.update_distances()
    return render(request, 'helpers/routespage.html')


def generate_routes(request):
    if "date" in request.GET:
        selected_date = request.GET["date"]
        date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()

        # try:
        generator = RoutesGenerator()
        result = generator.generate_routes(date_obj, selected_date)
        if result != False:
            return HttpResponse(f"<div>Routes generated for {selected_date}!</div>")
        else:
            return HttpResponse(f"<div>Routes maken niet gelukt. Distance matrix niet compleet.</div>")
        # except Exception as e:
        #     return HttpResponse(f"<div><h3>Error: </h3>{e}</div>")

    else:
        return render(request, 'helpers/routespage.html')


def copy_routes(request):
    # RouteCopier().copy_routes()
    return render(request, 'helpers/routespage.html')


def calculate_arrival_times(request):
    calculator = ArrivalTimeCalculator()
    selected_date = request.GET.get("date")
    route_id = request.GET.get("route_id")
    conversie_id = request.GET.get("conversie_id")
    # Build the query
    query = Q()
    if selected_date:
        query &= Q(date=selected_date)
    if route_id:
        query &= Q(id=route_id)
    if conversie_id:
        query &= Q(stops__order__ConversieID=conversie_id)
    routes_queryset = Route.objects.filter(query).distinct().order_by('name')
    calculator.calculate_arrival_times(routes_queryset)
    return HttpResponse(f"<div>Updated arrival times for query: {query}</div>")


@csrf_exempt
def update_route_delay(request, route_id):
    print('update', route_id)
    if request.method == "POST":
        delay = int(request.POST.get("delay", 0))  # Get delay from the form
        route = get_object_or_404(Route, pk=route_id)
        stops = Stop.objects.filter(route=route)

        for stop in stops:
            if stop.arrival_time:
                arrival_time = stop.arrival_time
                base_date = datetime.combine(datetime.today(), arrival_time)

                # Add the delay
                new_datetime = base_date + timedelta(minutes=delay)

                # Update stop.arrival_time with the new time
                stop.arrival_time = new_datetime.time()
                stop.save()
        #
        #     # Return updated stops as JSON
        #     updated_stops = list(stops.values("id", "sequence_number", "address", "arrival_time"))
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"})


def orders_overview(request):
    return render(request, 'info_pages/orders_overview.html')


def get_order_transactions(request):
    transaction_getter = Paasontbijt2024Transacties()
    orders_matrix = transaction_getter.fetch_and_print_orders()
    context = {'orders_matrix': orders_matrix}
    return render(request, 'info_pages/orders_overview.html', context)
