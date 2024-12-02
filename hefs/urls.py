from django.urls import path

from hefs.views import views
from hefs.views.map_views import show_map_views
from hefs.views.recipe_views import recipe_views

# from . import views
# from views.views import *
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

    path('productinfo', recipe_views.show_productinfo, name='productinfo'),
    path('halfproducten', recipe_views.show_halfproducten, name='halfproducten'),
    path('ingredienten', recipe_views.show_ingredienten, name='ingredienten'),
    path('ingredient-autocomplete/', recipe_views.ingredient_autocomplete, name='ingredient_autocomplete'),
    path('halfproduct-autocomplete/', recipe_views.halfproduct_autocomplete, name='halfproduct_autocomplete'),
    path('product-autocomplete/', recipe_views.product_autocomplete, name='product_autocomplete'),
    path('get-ingredients-for-halfproduct/', recipe_views.get_ingredients_for_halfproduct,
         name='get_ingredients_for_halfproduct'),
    path('get_halfproducts_and_ingredients/', recipe_views.get_halfproducts_and_ingredients,
         name='get_halfproducts_and_ingredients'),
    path('get_ingredients_list/', recipe_views.get_ingredients_list, name='get_ingredients_list'),

    path('calculate_coordinates', views.calculate_coordinates, name='calculate_coordinates'),
    path('update_distance_matrix', views.update_distance_matrix, name='update_distance_matrix'),
    path('generate_routes/', views.generate_routes, name='generate_routes'),
    path('calculate_arrival_times/', views.calculate_arrival_times, name='calculate_arrival_times'),
    path("map/", show_map_views.show_map, name="show_map"),

]
