from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('orderspage', views.orderspage, name='orderspage'),
    path('veh', views.show_veh, name='veh'),
    path('customerinfo', views.show_customerinfo, name='customerinfo'),
    path('get_orders', views.get_orders, name='get_orders'),
]