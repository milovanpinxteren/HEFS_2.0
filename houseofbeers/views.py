from django.http import HttpResponse
from django.shortcuts import render
from django_rq import job

from hefs.classes.shopify_sync.sync_table_updater import SyncTableUpdater
from hefs.models import AlgemeneInformatie
from hefs.views.views import show_busy
from houseofbeers.utils.calculators import group_orders_by_channel_and_tag
from houseofbeers.utils.shopify import get_shopify_orders


def show_sync_page(request):
    return render(request, 'helpers/sync_page.html')

def show_hob_orders_page(request):
    return render(request, 'helpers/hob_orders_page.html')

def start_product_sync(request):
    if request.method == 'POST':
        if request.environ.get('OS', '') == "Windows_NT":
            sync_hob()
            request.session['status'] = '100'
        else:
            AlgemeneInformatie.objects.filter(naam='status').delete()
            AlgemeneInformatie.objects.create(naam='status', waarde=1)
            sync_hob.delay()
            request.session['status'] = '100'
        return show_busy(request)
    else:
        return show_busy(request)
    print('start sync')
    return HttpResponse("Sync voltooid")


@job
def sync_hob():
    updater = SyncTableUpdater()
    updater.start_full_sync()


def show_taxes(request):
    print('showing taxes')
    if request.method == "POST":
        begin = request.POST.get('begin_date')
        end = request.POST.get('end_date')

        if not begin or not end:
            return HttpResponse("Start and end date are required", status=400)

        orders = get_shopify_orders(start_date=begin, end_date=end)
        grouped_data = group_orders_by_channel_and_tag(orders)

        # Render as HTML
        return render(request, "partials/tax_results.html", {
            "grouped_data": grouped_data
        })


    return HttpResponse("Invalid request", status=400)
