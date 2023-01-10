import random

from django.db import models

class NewOrders(models.Model):
    conversieID = models.IntegerField(default=0)
    besteldatum = models.DateTimeField(null=True, blank=True)
    afleverdatum = models.DateTimeField(null=True, blank=True)
    aflevertijd = models.TimeField(null=True, blank=True)
    verzendkosten = models.IntegerField(default=0, null=True, blank=True)
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
    conversieID = models.IntegerField(default=0)
    besteldatum = models.DateTimeField(null=True, blank=True)
    afleverdatum = models.DateTimeField(null=True, blank=True)
    aflevertijd = models.TimeField(null=True, blank=True)
    verzendkosten = models.IntegerField(default=0, null=True, blank=True)
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

class Orderline(models.Model):
    #TODO foreignkey vanuit orders
    conversieID = models.IntegerField(default=0)
    product = models.CharField(max_length=250, null=True, blank=True)
    productSKU = models.CharField(max_length=250, null=True, blank=True)
    aantal = models.IntegerField(default=0, null=True, blank=True)


class Productinfo(models.Model):
    class GangChoice(models.IntegerChoices):
        Amuse = 1
        Voorgerecht = 2
        Soep = 3
        Hoofdgerecht = 4
        Nagerecht = 5
        Bijgerecht = 6
        Dranken = 7
        Extra = 8
        Overig = 9

    productID = models.CharField(help_text="Alleen invullen als je geen automatisch gegenereerd nummer wil", max_length=5, primary_key=True, default='', blank=True)
    omschrijving = models.CharField(max_length=250)
    productcode = models.CharField(help_text="Alleen invullen als je geen automatisch gegenereerd nummer wil", max_length=3, default='', blank=True)
    productnaam = models.CharField(max_length=250)
    leverancier = models.CharField(max_length=250)
    verpakkingseenheid = models.IntegerField(default=0)
    gang = models.IntegerField(choices=GangChoice.choices)
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
            self.productID = str(self.gang) + str(self.productcode) + str(self.verpakkingseenheid)

        super(Productinfo, self).save()

for i in range(1,26):
    name = "Verpakkingscombinatie_" + str(i) + " keer besteld"
    Productinfo.add_to_class(name, models.CharField(max_length=300, default='', help_text="Bijvoorbeeld 4,3,2"))








class Productextra(models.Model):
    product = models.ForeignKey('Productinfo', on_delete=models.PROTECT, default='')
    productnaam = models.CharField(product, max_length=250, blank=True)
    extra_productnaam = models.ForeignKey(Productinfo, on_delete=models.CASCADE, related_name='productextra_extra_productnaam', default='', blank=True)
    # productnaam = models.CharField(max_length=250, choices=product_choice)
    # extra_productnaam = models.CharField(max_length=250, choices=product_choice)
    def __str__(self):
        return self.productnaam




class Orderextra(models.Model):
    productnaam = models.CharField(max_length=250)


class Gang(models.Model):
    gangnummer = models.CharField(max_length=1, default='')
    gangnaam = models.CharField(max_length=50, default='')


class Vaste_kosten(models.Model):
    kostennaam = models.CharField(max_length=30, default='')
    kostenomschrijving = models.CharField(max_length=300, default='-')
    kosten = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Variable_kosten(models.Model):
    kostennaam = models.CharField(max_length=30, default='')
    kostenomschrijving = models.CharField(max_length=300, default='-')
    kosten_per_eenheid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vermenigvuldiging = models.IntegerField(default=0, help_text='1=Per order, 2=Per hoofdgerecht')

class Percentuele_kosten(models.Model):
    kostennaam = models.CharField(max_length=30, default='')
    kostenomschrijving = models.CharField(max_length=300, default='-')
    percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class ApiUrls(models.Model):
    url = models.URLField(max_length=250)
    # userID
