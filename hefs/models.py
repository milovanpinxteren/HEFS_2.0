import random

from django.db import models
from django.contrib.postgres.fields import ArrayField



#############################################Orders below###############################################################
class VerzendOpties(models.Model):
    verzendoptie = models.CharField(max_length=250)
    verzendkosten = models.DecimalField(default=0, null=True, blank=True, decimal_places=2, max_digits=6)
    verzenddatum = models.DateField(null=True, blank=True)

class NewOrders(models.Model):
    conversieID = models.IntegerField(default=0, db_index=True)
    besteldatum = models.DateTimeField(null=True, blank=True)
    verzendoptie = models.ForeignKey(VerzendOpties, on_delete=models.CASCADE, default='', blank=True)
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
    besteldatum = models.DateTimeField(null=True, blank=True)
    afleverdatum = models.DateField(null=True, blank=True)
    aflevertijd = models.TimeField(null=True, blank=True)
    verzendkosten = models.DecimalField(default=0, null=True, blank=True, decimal_places=2, max_digits=6)
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
    routenr = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.conversieID)

class Orderline(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, default='', blank=True)
    product = models.CharField(max_length=250, null=True, blank=True)
    productSKU = models.CharField(max_length=250, null=True, blank=True)
    aantal = models.IntegerField(default=0, null=True, blank=True)


#############################################Verpakkingsmodels below####################################################

class VerpakkingsMogelijkheden(models.Model):
    naam = models.CharField(max_length=250)

    def __str__(self):
        return self.naam


class VerpakkingsCombinaties(models.Model):
    verpakkingsmogelijkheid = models.ForeignKey(VerpakkingsMogelijkheden, on_delete=models.CASCADE)
    bestelde_hoeveelheid = models.FloatField()
    verpakkingscombinatie = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.bestelde_hoeveelheid} -> {self.verpakkingscombinatie}"



#############################################Products below#############################################################

class Gang(models.Model):
    gangnaam = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.gangnaam

class Productinfo(models.Model):
    productID = models.CharField(help_text="Alleen invullen als je geen automatisch gegenereerd nummer wil", max_length=5, primary_key=True, default='', blank=True, db_index=True)
    omschrijving = models.CharField(max_length=250)
    productcode = models.CharField(help_text="Alleen invullen als je geen automatisch gegenereerd nummer wil", max_length=3, default='', blank=True, db_index=True)
    productnaam = models.CharField(max_length=250)
    leverancier = models.CharField(max_length=250)
    verpakkingseenheid = models.IntegerField(default=0)
    verpakkingscombinatie = models.ForeignKey(VerpakkingsMogelijkheden, on_delete=models.PROTECT, related_name='VerpakkingsMogelijkheden', default='', blank=True)
    gang = models.ForeignKey(Gang, on_delete=models.PROTECT, related_name='gang', default='', blank=True)
    picknaam = models.CharField(max_length=250)
    pickvolgorde = models.IntegerField(default=0)
    productiekosten = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    verkoop_incl_btw = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    verkoop_excl_btw = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    verpakkingsoort = models.CharField(max_length=15, default='')
    afmeting_lengte_mm = models.IntegerField(default=0)
    afmeting_breedte_mm = models.IntegerField(default=0)
    afmeting_hoogte_mm = models.IntegerField(default=0)

    def __str__(self):
        return self.productnaam

    def save(self):
        if not (self.productcode or self.productcode):
            self.productcode = random.randint(99, 999)
            self.productID = str(self.gang.id) + str(self.productcode) + str(self.verpakkingseenheid)

        super(Productinfo, self).save()


#############################################Extras below###############################################################


class Productextra(models.Model):
    productnaam = models.ForeignKey(Productinfo, on_delete=models.PROTECT, related_name='productextra_productnaam', default='', blank=True)
    extra_productnaam = models.ForeignKey(Productinfo, on_delete=models.PROTECT, related_name='productextra_extra_productnaam', default='', blank=True)



class Orderextra(models.Model):
    productnaam = models.ForeignKey(Productinfo, on_delete=models.PROTECT, related_name='orderextra_productnaam', default='', blank=True)



#############################################Pick models below##########################################################

class PickOrders(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)


class PickItems(models.Model):
    pick_order = models.ForeignKey(PickOrders, on_delete=models.CASCADE)
    product = models.ForeignKey(Productinfo, null=True, on_delete=models.SET_NULL)
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

class ApiUrls(models.Model):
    api = models.URLField(max_length=250)
    user_id = models.IntegerField(default=0)
    begindatum = models.DateField(null=True)
    organisatieIDs = ArrayField(models.IntegerField(default=0), blank=True, default=[])

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

class JSONData(models.Model):
    key = models.CharField(max_length=25)
    value = models.JSONField()