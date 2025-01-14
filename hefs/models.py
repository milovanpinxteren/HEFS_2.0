import random

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


#############################################Choices below###############################################################
class MeasurementUnit(models.TextChoices):
    KG = 'KG', 'Kilogram'
    ST = 'ST', 'per stuk'
    LT = 'LT', 'Liter'

class BTW(models.TextChoices):
    H = 'H', 'Hoog (21%)'
    L = 'L', 'Laag (9%)'
    G = '0', 'Geen/0'
#############################################Orders below###############################################################
class VerzendOpties(models.Model):
    verzendoptie = models.CharField(max_length=250)
    verzendkosten = models.DecimalField(default=0, null=True, blank=True, decimal_places=2, max_digits=6)
    verzenddatum = models.DateField(null=True, blank=True)

class NewOrders(models.Model):
    conversieID = models.IntegerField(default=0, db_index=True)
    shopifyID = models.BigIntegerField(default=0)
    besteldatum = models.DateTimeField(null=True, blank=True)
    verzendoptie = models.ForeignKey(VerzendOpties, on_delete=models.CASCADE, null=True, blank=True)
    afleverdatum = models.DateTimeField(null=True, blank=True, db_index=True)
    aflevertijd = models.TimeField(null=True, blank=True)
    verzendkosten = models.DecimalField(default=0, null=True, blank=True, decimal_places=2, max_digits=6)
    korting = models.IntegerField(default=0, null=True, blank=True)
    orderprijs = models.DecimalField(default=0, null=True, blank=True, decimal_places=2, max_digits=6)
    totaal = models.IntegerField(default=0, null=True, blank=True)
    aantal = models.IntegerField(default=0, null=True, blank=True)
    product = models.CharField(max_length=250, null=True, blank=True)
    productSKU = models.CharField(max_length=250, null=True, blank=True)
    organisatieID = models.IntegerField(default=0, null=True, blank=True)
    organisatienaam = models.CharField(max_length=250, null=True, blank=True)
    voornaam = models.CharField(max_length=250, null=True, blank=True)
    achternaam = models.CharField(max_length=250, null=True, blank=True)
    tussenvoegsel = models.CharField(max_length=250, null=True, blank=True)
    emailadres = models.CharField(max_length=250, null=True, blank=True)
    telefoonnummer = models.CharField(max_length=250, null=True, blank=True)
    straatnaam = models.CharField(max_length=250, null=True, blank=True)
    huisnummer = models.CharField(max_length=250, null=True, blank=True)
    postcode = models.CharField(max_length=250, null=True, blank=True)
    plaats = models.CharField(max_length=250, null=True, blank=True)
    land = models.CharField(max_length=250, null=True, blank=True)
    postadres_straatnaam = models.CharField(max_length=250, null=True, blank=True)
    postadres_huisnummer = models.CharField(max_length=250, null=True, blank=True)
    postadres_postcode = models.CharField(max_length=250, null=True, blank=True)
    postadres_plaats = models.CharField(max_length=250, null=True, blank=True)
    postadres_land = models.CharField(max_length=250, null=True, blank=True)
    opmerkingen = models.CharField(max_length=2500, null=True, blank=True)


class Orders(models.Model):
    conversieID = models.IntegerField(default=0, db_index=True)
    shopifyID = models.BigIntegerField(default=0)
    besteldatum = models.DateTimeField(null=True, blank=True)
    afleverdatum = models.DateField(null=True, blank=True)
    aflevertijd = models.TimeField(null=True, blank=True)
    verzendkosten = models.DecimalField(default=0, null=True, blank=True, decimal_places=2, max_digits=6)
    verzendoptie = models.ForeignKey(VerzendOpties, on_delete=models.CASCADE, null=True, blank=True)
    korting = models.IntegerField(default=0, null=True, blank=True)
    orderprijs = models.DecimalField(default=0, null=True, blank=True, decimal_places=2, max_digits=6)
    organisatieID = models.IntegerField(default=0, null=True, blank=True)
    organisatienaam = models.CharField(max_length=250, null=True, blank=True)
    voornaam = models.CharField(max_length=250, null=True, blank=True)
    achternaam = models.CharField(max_length=250, null=True, blank=True)
    tussenvoegsel = models.CharField(max_length=250, null=True, blank=True)
    emailadres = models.CharField(max_length=250, null=True, blank=True)
    telefoonnummer = models.CharField(max_length=250, null=True, blank=True)
    straatnaam = models.CharField(max_length=250, null=True, blank=True)
    huisnummer = models.CharField(max_length=250, null=True, blank=True)
    postcode = models.CharField(max_length=250, null=True, blank=True)
    plaats = models.CharField(max_length=250, null=True, blank=True)
    land = models.CharField(max_length=250, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    routenr = models.IntegerField(null=True, blank=True)
    opmerkingen = models.CharField(max_length=2500, null=True, blank=True)

    def __str__(self):
        return str(self.conversieID)

class Orderline(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, blank=True)
    product = models.CharField(max_length=250, null=True, blank=True)
    productSKU = models.CharField(max_length=250, null=True, blank=True)
    aantal = models.IntegerField(default=0, null=True, blank=True)


#############################################Routes below#############################################################

class DistanceMatrix(models.Model):
    origin = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='distances_from')
    destination = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='distances_to')
    distance_meters = models.IntegerField(null=True)

class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vehicles")
    vehicle_number = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()  # Example: max capacity in kg or volume
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vehicle {self.vehicle_number} driven by {self.user.username}"


class Route(models.Model):
    name = models.CharField(max_length=100, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="routes")
    date = models.DateField()
    departure_time = models.TimeField(null=True, blank=True)
    google_maps_link = models.URLField(null=True, blank=True, max_length=1000)  # Add this field
    created_at = models.DateTimeField(auto_now_add=True)
    total_distance = models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
    total_travel_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Route {self.name} on {self.date}"


class Stop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="stops")
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="stop")
    sequence_number = models.PositiveIntegerField()  # Order of the stop in the route
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    visited = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Stop {self.sequence_number} on {self.route.name}"

#############################################Verpakkingsmodels below####################################################

class VerpakkingsMogelijkheden(models.Model):
    naam = models.CharField(max_length=250)

    def __str__(self):
        return self.naam


class VerpakkingsCombinaties(models.Model):
    verpakkingsmogelijkheid = models.ForeignKey(VerpakkingsMogelijkheden, on_delete=models.CASCADE, null=True, blank=True)
    bestelde_hoeveelheid = models.FloatField()
    verpakkingscombinatie = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.bestelde_hoeveelheid} -> {self.verpakkingscombinatie}"


class VerpakkingsSoort(models.Model):
    naam = models.CharField(max_length=250)
    afmeting_lengte_mm = models.IntegerField(default=0)
    afmeting_breedte_mm = models.IntegerField(default=0)
    afmeting_hoogte_mm = models.IntegerField(default=0)
    stuks_per_krat = models.IntegerField(default=0)
    kosten_per_eenheid = models.DecimalField(default=0, decimal_places=2, max_digits=6)

    def __str__(self):
        return self.naam


#############################################Products below#############################################################

class Gang(models.Model):
    gangnaam = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.gangnaam

class Leveranciers(models.Model):
    naam = models.CharField(max_length=250, blank=True, null=True)
    emailadres = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.naam

class Productinfo(models.Model):
    productID = models.CharField(help_text="Alleen invullen als je geen automatisch gegenereerd nummer wil", max_length=5, primary_key=True, default='', blank=True, db_index=True)
    omschrijving = models.CharField(max_length=250)
    productcode = models.CharField(help_text="Alleen invullen als je geen automatisch gegenereerd nummer wil", max_length=3, default='', blank=True, db_index=True)
    productnaam = models.CharField(max_length=250)
    leverancier = models.ForeignKey(Leveranciers, on_delete=models.PROTECT, null=True, blank=True)
    verpakkingseenheid = models.IntegerField(default=0)
    verpakkingscombinatie = models.ForeignKey(VerpakkingsMogelijkheden, on_delete=models.PROTECT, related_name='VerpakkingsMogelijkheden', null=True, blank=True)
    gang = models.ForeignKey(Gang, on_delete=models.PROTECT, related_name='gang', null=True, blank=True)
    picknaam = models.CharField(max_length=250)
    pickvolgorde = models.IntegerField(default=0)
    bereidingskosten = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    # btw_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="9% is 1.09")
    btw = models.CharField(choices=BTW.choices, max_length=1, null=True, blank=True)
    verkoop_incl_btw = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    verkoop_excl_btw = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    verpakkingsoort = models.ForeignKey(VerpakkingsSoort, on_delete=models.PROTECT, null=True, blank=True)
    bereidingskosten_per_eenheid = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    etiket = models.BinaryField(blank=True, null=True)


    def __str__(self):
        return self.picknaam

    class Meta:
        ordering = ['productnaam']  # Sorts by product name alphabetically

    def save(self):
        if not (self.productcode or self.productcode):
            self.productcode = random.randint(99, 999)
            self.productID = str(self.gang.id) + str(self.productcode) + str(self.verpakkingseenheid)

        super(Productinfo, self).save()


class Halfproducten(models.Model):
    naam = models.CharField(max_length=250, default='')
    product = models.ForeignKey(Productinfo, on_delete=models.PROTECT, null=True, blank=True)
    meeteenheid = models.CharField(choices=MeasurementUnit.choices, default=MeasurementUnit.KG, max_length=2)
    bruikbare_hoeveelheid = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    bereidingswijze = models.TextField(default='')
    bereidingskosten_per_eenheid = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text='Per KG/L/Stuk')
    leverancier = models.ForeignKey(Leveranciers, on_delete=models.PROTECT, null=True, blank=True)
    verpakkingsoort = models.ForeignKey(VerpakkingsSoort, on_delete=models.PROTECT, null=True, blank=True)
    btw = models.CharField(choices=BTW.choices, max_length=1, null=True, blank=True)

    def __str__(self):
        return self.naam


class Ingredienten(models.Model):
    naam = models.CharField(max_length=250, default='')
    meeteenheid = models.CharField(choices=MeasurementUnit.choices, default=MeasurementUnit.KG, max_length=2)
    kosten_per_eenheid = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text='Per KG/L/Stuk')
    leverancier = models.ForeignKey(Leveranciers, on_delete=models.PROTECT, null=True, blank=True)
    btw = models.CharField(choices=BTW.choices, max_length=1, null=True, blank=True)
    verpakkingsoort = models.ForeignKey(VerpakkingsSoort, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.naam


class ProductenHalfproducts(models.Model):
    product = models.ForeignKey(Productinfo, on_delete=models.CASCADE, null=True, blank=True)
    productcode = models.CharField(max_length=3, default=0)
    halfproduct = models.ForeignKey(Halfproducten, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=6, decimal_places=3, default=0)

    class Meta:
        unique_together = ('product', 'halfproduct',)  # Ensures uniqueness of ingredient for each halfproduct

    def __str__(self):
        return f"{self.product} - {self.halfproduct} - {self.quantity}"

class HalfproductenIngredienten(models.Model):
    halfproduct = models.ForeignKey(Halfproducten, on_delete=models.CASCADE, null=True, blank=True)
    ingredient = models.ForeignKey(Ingredienten, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=6, decimal_places=3, default=0)

    class Meta:
        unique_together = ('halfproduct', 'ingredient',)  # Ensures uniqueness of ingredient for each halfproduct

    def __str__(self):
        return f"{self.halfproduct} - {self.ingredient} - {self.quantity}"


class ProductenIngredienten(models.Model):
    product = models.ForeignKey(Productinfo, on_delete=models.CASCADE, null=True, blank=True)
    productcode = models.CharField(max_length=3, default=0)
    ingredient = models.ForeignKey(Ingredienten, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.DecimalField(max_digits=6, decimal_places=3, default=0)

    class Meta:
        unique_together = ('product', 'ingredient',)  # Ensures uniqueness of ingredient for each halfproduct

    def __str__(self):
        return f"{self.product} - {self.ingredient} - {self.quantity}"


class AlreadyProduced(models.Model):
    product = models.ForeignKey(Productinfo, on_delete=models.SET_NULL, null=True, blank=True)
    halfproduct = models.ForeignKey(Halfproducten, on_delete=models.SET_NULL, null=True, blank=True)
    ingredient = models.ForeignKey(Ingredienten, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()

    def save(self, *args, **kwargs):
        # Ensure only one of product, half_product, ingredient is set
        model_count = sum([1 for val in [self.product, self.halfproduct, self.ingredient] if val is not None])
        if model_count != 1:
            raise Exception("One and only one of Product, Halfproduct, Ingredient must be set.")
        super(AlreadyProduced, self).save(*args, **kwargs)



#############################################Extras below###############################################################


class Productextra(models.Model):
    productnaam = models.ForeignKey(Productinfo, on_delete=models.PROTECT, related_name='productextra_productnaam', null=True, blank=True)
    extra_productnaam = models.ForeignKey(Productinfo, on_delete=models.PROTECT, related_name='productextra_extra_productnaam', null=True, blank=True)

    class Meta:
        ordering = ['productnaam']  # Sorts by product name alphabetically

class Orderextra(models.Model):
    productnaam = models.ForeignKey(Productinfo, on_delete=models.PROTECT, related_name='orderextra_productnaam', blank=True, null=True)

    class Meta:
        ordering = ['productnaam']  # Sorts by product name alphabetically


#############################################Pick models below##########################################################

class PickOrders(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, blank=True)


class PickItems(models.Model):
    pick_order = models.ForeignKey(PickOrders, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Productinfo, on_delete=models.SET_NULL, null=True, blank=True)
    omschrijving = models.CharField(max_length=250, null=True)
    hoeveelheid = models.FloatField()

    def __str__(self):
        return f"{self.hoeveelheid} {self.product}"

#############################################Kosten models below########################################################


class VasteKosten(models.Model):
    kostennaam = models.CharField(max_length=30, default='')
    kostenomschrijving = models.CharField(max_length=300, default='-')
    kosten = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class VariableKosten(models.Model):
    kostennaam = models.CharField(max_length=30, default='')
    kostenomschrijving = models.CharField(max_length=300, default='-')
    kosten_per_eenheid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vermenigvuldiging = models.IntegerField(default=0, help_text='1=Per order, 2=Per hoofdgerecht')

class PercentueleKosten(models.Model):
    kostennaam = models.CharField(max_length=30, default='')
    kostenomschrijving = models.CharField(max_length=300, default='-')
    percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)


#############################################General models below#######################################################

class AlgemeneInformatie(models.Model):
    naam = models.CharField(max_length=300, default='')
    waarde = models.IntegerField(default=0)
    text = models.CharField(max_length=800, default='')

class ApiUrls(models.Model):
    api = models.URLField(max_length=250)
    user_id = models.IntegerField(default=0)
    begindatum = models.DateField(null=True)
    organisatieIDs = ArrayField(models.IntegerField(default=0), blank=True, default=[])


class LeverancierUserLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    leverancier = models.ForeignKey(Leveranciers, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.leverancier.naam}"

class Customers(models.Model):
    emailadres = models.CharField(max_length=300, default='', unique=True)
    voornaam = models.CharField(max_length=300, default='', null=True)
    tussenvoegsel = models.CharField(max_length=300, default='', null=True)
    achternaam = models.CharField(max_length=300, default='', null=True)
    postcode = models.CharField(max_length=300, default='', null=True)
    plaats = models.CharField(max_length=300, default='', null=True)
    ordered_2020 = models.BinaryField(blank=True, default=0, null=True)
    ordered_2021 = models.BinaryField(blank=True, default=0, null=True)
    ordered_2022 = models.BinaryField(blank=True, default=0, null=True)
    ordered_2023 = models.BinaryField(blank=True, default=0, null=True)
    ordered_2024 = models.BinaryField(blank=True, null=True)

class JSONData(models.Model):
    key = models.CharField(max_length=25)
    value = models.JSONField()


#############################################HOB/Gerijptebieren########################################################

class ErrorLogDataGerijptebieren(models.Model):
    error_message = models.CharField(max_length=300, default='', null=True)
    timestamp = models.DateTimeField(null=True, blank=True)


class TerminalLinks(models.Model):
    shop_id = models.CharField(max_length=255, unique=True)
    user_id = models.CharField(max_length=255)
    shop_domain = models.CharField(max_length=255, unique=True)
    location_id = models.CharField(max_length=255, blank=True, null=True)
    staff_member_id = models.CharField(max_length=255, blank=True, null=True)
    terminal_id = models.CharField(max_length=255, blank=True, null=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.shop_domain


# class Products(models.Model):
#     title = models.CharField(max_length=250, default='')
#     description = models.CharField(max_length=5000, default='')
#     price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class FeeProducts(models.Model):
    shop_url = models.CharField(max_length=255, unique=True)
    tag_name = models.CharField(max_length=255, unique=True)
    fee_variant_id = models.CharField(max_length=255, unique=True)
