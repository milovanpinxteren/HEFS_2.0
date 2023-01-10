from django.contrib import admin
from .models import Productinfo, Productextra, Vaste_kosten


@admin.register(Productinfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ['omschrijving', 'productcode', 'productID', 'picknaam', 'productnaam',
                    'leverancier', 'verpakkingseenheid', 'gang']
    search_fields = ("omschrijving__contains",)

@admin.register(Productextra)
class ProductExtraAdmin(admin.ModelAdmin):
    list_display = ['product', 'extra_productnaam']
    search_fields = ("product__productnaam",)

@admin.register(Vaste_kosten)
class VasteKostenAdmin(admin.ModelAdmin):
    list_display = ['kostennaam', 'kostenomschrijving', 'kosten']