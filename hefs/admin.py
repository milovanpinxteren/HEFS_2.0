from django.contrib import admin
from .models import Productinfo, Productextra, VerpakkingsMogelijkheden, VerpakkingsCombinaties, \
    VasteKosten, VariableKosten, PercentueleKosten, Gang, Orderextra


@admin.register(Productinfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ['omschrijving', 'verpakkingscombinatie', 'productID', 'picknaam', 'productnaam',
                    'leverancier', 'gang']
    search_fields = ("omschrijving__contains",)

@admin.register(Productextra)
class ProductExtraAdmin(admin.ModelAdmin):
    list_display = ['productnaam', 'extra_productnaam']
    search_fields = ("product__productnaam",)

@admin.register(Orderextra)
class OrderExtraAdmin(admin.ModelAdmin):
    list_display = ['productnaam']
    search_fields = ("product__productnaam",)

@admin.register(VerpakkingsMogelijkheden)
class VerpakkingsMogelijkhedenAdmin(admin.ModelAdmin):
    list_display = ['naam']
    search_fields = ("naam__contains",)

@admin.register(VerpakkingsCombinaties)
class VerpakkingsCombinatiesAdmin(admin.ModelAdmin):
    list_display = ['verpakkingsmogelijkheid', 'bestelde_hoeveelheid', 'verpakkingscombinatie']
    search_fields = ("verpakkingsmogelijkheid__contains",)

@admin.register(Gang)
class GangAdmin(admin.ModelAdmin):
    list_display = ['gangnaam']

@admin.register(VasteKosten)
class VasteKostenAdmin(admin.ModelAdmin):
    list_display = ['kostennaam', 'kostenomschrijving', 'kosten']

@admin.register(VariableKosten)
class VasteKostenAdmin(admin.ModelAdmin):
    list_display = ['kostennaam', 'kostenomschrijving', 'kosten_per_eenheid']

@admin.register(PercentueleKosten)
class VasteKostenAdmin(admin.ModelAdmin):
    list_display = ['kostennaam', 'kostenomschrijving', 'percentage']