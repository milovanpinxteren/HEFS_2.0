from django.contrib import admin
from .models import Productinfo, Productextra


@admin.register(Productinfo)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['omschrijving', 'productcode', 'productID', 'picknaam', 'productnaam',
                    'leverancier', 'verpakkingseenheid', 'gang']
    search_fields = ("omschrijving__contains",)

@admin.register(Productextra)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['productnaam', 'extra_productnaam']