from django.urls import path
from houseofbeers.views import *

app_name = "houseofbeers"

urlpatterns = [
    path('show_sync_page', show_sync_page, name='show_sync_page'),
    path('show_hob_orders_page', show_hob_orders_page, name='show_hob_orders_page'),
    path('start_product_sync', start_product_sync, name='start_product_sync'),
    path('show_taxes', show_taxes, name='show_taxes'),
    path("taxes/status/<str:job_id>/", check_taxes_status, name="check_taxes_status")

]
