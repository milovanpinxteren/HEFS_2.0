from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('veh', views.show_veh, name='veh'),
    path('update-general-numbers', views.update_general_numbers),
    path('customerinfo', views.show_customerinfo, name='customerinfo'),
    path('customerlocationplot', views.show_customerlocationplot, name='customerlocationplot'),
    path('getorderspage', views.getorderspage, name='getorderspage'),
    path('makeorderspage', views.makeorderspage, name='makeorderspage'),
    path('get_orders', views.get_orders, name='get_orders'),
    path('pickbonnen_page', views.pickbonnen_page, name='pickbonnen_page'),
    path('get_pickbonnen', views.get_pickbonnen, name='get_pickbonnen'),
    path('financial_overview_page', views.financial_overview_page, name='financial_overview_page'),
    path('facturen_page', views.facturen_page, name='facturen_page'),
    path('get_status', views.get_status, name='get_status'),
    path('recieve_webhook', views.recieve_webhook, name='recieve_webhook'),

    path('handle_alterated_new_orders', views.handle_alterated_new_orders, name='handle_alterated_new_orders'),

]
