from django.contrib import admin

from .models import Productinfo, Productextra, VerpakkingsMogelijkheden, VerpakkingsCombinaties, \
    VasteKosten, VariableKosten, PercentueleKosten, Gang, Orderextra, Orders, ApiUrls, AlgemeneInformatie, Orderline, \
    VerzendOpties, JSONData, Halfproducten, Ingredienten, HalfproductenIngredienten, AlreadyProduced, \
    ProductenIngredienten, VerpakkingsSoort, ProductenHalfproducts, LeverancierUserLink, Customers, Leveranciers, \
    Vehicle, Route, Stop, TerminalLinks, FeeProducts, SyncInfo


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
    autocomplete_fields = ["order"]  # Enables search for the related 'order'

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


@admin.register(Leveranciers)
class LeveranciersAdmin(admin.ModelAdmin):
    list_display = ['naam', 'emailadres']


@admin.register(LeverancierUserLink)
class LeverancierUserLinkAdmin(admin.ModelAdmin):
    list_display = ['user', 'leverancier']


@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    list_display = ['emailadres', 'achternaam', 'ordered_2020', 'ordered_2021', 'ordered_2022', 'ordered_2023',
                    'ordered_2024']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle_number', 'capacity', 'created_at']
    search_fields = ['vehicle_number', 'user__username']
    list_filter = ['capacity', 'created_at']


class StopInline(admin.TabularInline):
    model = Stop
    extra = 1  # Number of blank stops to display for addition
    fields = ['order', 'sequence_number', 'arrival_time', 'departure_time', 'visited', 'notes']
    ordering = ['sequence_number']  # Order stops by sequence_number
    show_change_link = True  # Adds a link to edit stop details
    autocomplete_fields = ['order']  # Enable search for the 'order' field


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'vehicle', 'date', 'created_at']
    search_fields = ['name', 'vehicle__vehicle_number']
    list_filter = ['date', 'created_at']
    inlines = [StopInline]  # Add stops inline in the route admin


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ['route', 'order', 'sequence_number', 'arrival_time',
                    'departure_time', 'notes']
    search_fields = ['route__name', 'order__order_number']
    list_filter = ['route', 'sequence_number']
    autocomplete_fields = ['order']  # Enable search for the 'order' field


@admin.register(TerminalLinks)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('shop_id', 'user_id', 'shop_domain', 'location_id', 'staff_member_id', 'terminal_id')
    search_fields = ('shop_id', 'shop_domain', 'user_id')

@admin.register(FeeProducts)
class FeeProductsAdmin(admin.ModelAdmin):
    list_display = ('shop_url', 'tag_name', 'fee_variant_id')
    search_fields = ('shop_url', 'tag_name')

@admin.register(SyncInfo)
class SyncInfoAdmin(admin.ModelAdmin):
    list_display = ('hob_product_title', 'hob_product_handle', 'geb_product_title', 'geb_product_handle', 'quantity')
    search_fields = ('hob_product_title', 'geb_product_title')