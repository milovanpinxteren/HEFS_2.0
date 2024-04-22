from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('veh', views.show_veh, name='veh'),
    path('halfproducten', views.show_halfproducten, name='halfproducten'),
    path('update-general-numbers', views.update_general_numbers),
    path('customerinfo', views.show_customerinfo, name='customerinfo'),
    path('customerlocationplot', views.show_customerlocationplot, name='customerlocationplot'),
    path('getorderspage', views.getorderspage, name='getorderspage'),
    path('makeorderspage', views.makeorderspage, name='makeorderspage'),
    path('get_orders', views.get_orders, name='get_orders'),
    path('pickbonnen_page', views.pickbonnen_page, name='pickbonnen_page'),
    path('get_pickbonnen', views.get_pickbonnen, name='get_pickbonnen'),
    path('download_pickbonnen', views.download_pickbonnen, name='download_pickbonnen'),
    path('routes_page', views.routes_page, name='routes_page'),
    path('financial_overview_page', views.financial_overview_page, name='financial_overview_page'),
    path('facturen_page', views.facturen_page, name='facturen_page'),
    path('copy_routes', views.copy_routes, name='copy_routes'),

    path('orders_overview', views.orders_overview, name='orders_overview'),
    path('get_order_transactions', views.get_order_transactions, name='get_order_transactions'),
    path('get_status', views.get_status, name='get_status'),
    path('recieve_webhook', views.recieve_webhook, name='recieve_webhook'),
    path('show_sync_page', views.show_sync_page, name='show_sync_page'),
    path('start_product_sync', views.start_product_sync, name='start_product_sync'),

    path('handle_alterated_new_orders', views.handle_alterated_new_orders, name='handle_alterated_new_orders'),

]
