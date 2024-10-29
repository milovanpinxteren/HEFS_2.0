from django.contrib import admin
from .models import Productinfo, Productextra, VerpakkingsMogelijkheden, VerpakkingsCombinaties, \
    VasteKosten, VariableKosten, PercentueleKosten, Gang, Orderextra, Orders, ApiUrls, AlgemeneInformatie, Orderline, \
    VerzendOpties, JSONData, Halfproducten, Ingredienten, HalfproductenIngredienten, AlreadyProduced, \
    ProductenIngredienten, VerpakkingsSoort, ProductenHalfproducts, LeverancierUserLink, Customers


@admin.register(JSONData)
class JSONDataJSONDataAdmin(admin.ModelAdmin):
    list_display = ['key']


@admin.register(VerzendOpties)
class VerzendOptiesAdmin(admin.ModelAdmin):
    list_display = ['verzendoptie', 'verzendkosten']


@admin.register(Orders)
class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversieID', 'besteldatum', 'afleverdatum', 'orderprijs', 'voornaam',
                    'achternaam']
    search_fields = ("conversieID__contains", "voornaam__contains", "achternaam__contains")


@admin.register(Orderline)
class OrderlineAdmin(admin.ModelAdmin):
    list_display = ["conversieID", 'product', 'productSKU', 'aantal']
    search_fields = ("order_id__conversieID__contains", "product__contains")

    def conversieID(self, obj):
        return obj.order.conversieID


class HalfproductenIngredientenInline(admin.TabularInline):
    model = HalfproductenIngredienten
    extra = 1


@admin.register(Ingredienten)
class IngredientenAdmin(admin.ModelAdmin):
    list_display = ('naam', 'meeteenheid', 'kosten_per_eenheid')
    search_fields = ('naam', 'productinfo__naam')  # Assuming 'naam' is a field in Productinfo
    inlines = [HalfproductenIngredientenInline]


@admin.register(Productinfo)
class ProductInfoAdmin(admin.ModelAdmin):
    # inlines = [IngredientenInline, ]
    list_display = ['omschrijving', 'verpakkingscombinatie', 'productID', 'picknaam', 'productnaam',
                    'leverancier', 'gang']
    search_fields = ("omschrijving__contains",)
    # exclude = ('ingredienten',)


@admin.register(Halfproducten)
class HalfproductenAdmin(admin.ModelAdmin):
    inlines = [HalfproductenIngredientenInline]
    exclude = ('ingredienten',)
    list_display = ('naam', 'product', 'meeteenheid', 'bereidingswijze', 'bereidingskosten_per_eenheid')
    # autocomplete_fields = ['ingredienten']


@admin.register(AlreadyProduced)
class AlreadyProducedAdmin(admin.ModelAdmin):
    list_display = ['product', 'halfproduct', 'ingredient', 'quantity']


@admin.register(ProductenHalfproducts)
class ProductenHalfproductsAdmin(admin.ModelAdmin):
    list_display = ['product', 'halfproduct', 'quantity']


@admin.register(HalfproductenIngredienten)
class HalfproductenIngredientenAdmin(admin.ModelAdmin):
    list_display = ['halfproduct', 'ingredient', 'quantity']


@admin.register(ProductenIngredienten)
class ProductenIngredientenAdmin(admin.ModelAdmin):
    list_display = ['product', 'ingredient', 'quantity']


@admin.register(Productextra)
class ProductExtraAdmin(admin.ModelAdmin):
    list_display = ['productnaam', 'extra_productnaam']
    # search_fields = ("product__productnaam",)
    search_fields = ["productnaam__productnaam__icontains", "productnaam__omschrijving__icontains",
                     "extra_productnaam__productnaam__icontains", "extra_productnaam__omschrijving__icontains"]
    autocomplete_fields = ['productnaam', 'extra_productnaam']  # Enables autocomplete


@admin.register(Orderextra)
class OrderExtraAdmin(admin.ModelAdmin):
    list_display = ['productnaam']
    search_fields = ("product__productnaam",)


@admin.register(VerpakkingsSoort)
class VerpakkingsSoortAdmin(admin.ModelAdmin):
    list_display = ['naam']
    search_fields = ("naam__contains",)


@admin.register(VerpakkingsMogelijkheden)
class VerpakkingsMogelijkhedenAdmin(admin.ModelAdmin):
    list_display = ['naam']
    search_fields = ("naam__contains",)


@admin.register(VerpakkingsCombinaties)
class VerpakkingsCombinatiesAdmin(admin.ModelAdmin):
    list_display = ['verpakkingsmogelijkheid', 'bestelde_hoeveelheid', 'verpakkingscombinatie']
    search_fields = ("verpakkingsmogelijkheid_id__naam",)


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


@admin.register(ApiUrls)
class ApiUrlAdmin(admin.ModelAdmin):
    list_display = ['api', 'organisatieIDs']


@admin.register(AlgemeneInformatie)
class AlgemeneInformatieAdmin(admin.ModelAdmin):
    list_display = ['naam', 'waarde']


@admin.register(LeverancierUserLink)
class LeverancierUserLinkAdmin(admin.ModelAdmin):
    list_display = ['user', 'leverancier']


@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    list_display = ['emailadres', 'achternaam', 'ordered_2020', 'ordered_2021', 'ordered_2022', 'ordered_2023',
                    'ordered_2024']
