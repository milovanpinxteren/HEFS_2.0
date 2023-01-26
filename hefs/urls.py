from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('veh', views.show_veh, name='veh'),
    path('customerinfo', views.show_customerinfo, name='customerinfo'),
    path('getorderspage', views.getorderspage, name='getorderspage'),
    path('get_orders', views.get_orders, name='get_orders'),
    path('pickbonnen_page', views.pickbonnen_page, name='pickbonnen_page'),
    path('get_pickbonnen', views.get_pickbonnen, name='get_pickbonnen'),
    path('financial_overview_page', views.financial_overview_page, name='financial_overview_page'),


]