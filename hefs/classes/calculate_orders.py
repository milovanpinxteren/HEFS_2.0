from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum

from hefs.models import Orders, PickOrders, Orderline, PickItems, Productextra, Productinfo, \
    VerpakkingsCombinaties, Orderextra, AlgemeneInformatie


class CalculateOrders():
    def __init__(self):
        print('CALCULATE ORDERS')
        PickOrders.objects.all().delete()
        PickItems.objects.all().delete()
        self.make_pickfile()
        self.optimize_picks()
        self.calculate_variables()

    def make_pickfile(self):
        print('MAKE PICKFILE')
        orders = Orders.objects.all()
        for order in orders:
            PickOrders.objects.create(order=order)
            self.make_order_extras(order)

        for self.pickorder in PickOrders.objects.all():
            self.pickorderlines = Orderline.objects.filter(order=self.pickorder.order_id)
            for product in self.pickorderlines:
                self.make_picks(product, 'Geen productextra', 'Geen productextra')
            self.make_product_extras(self.pickorderlines)

    def make_picks(self, product, aantal, order_id):
        if aantal == 'Geen productextra':
            bestelde_hoeveelheid = product.aantal
            productSKU = product.productSKU
            order_id = product.order_id
        else:  # if it is a productextra
            bestelde_hoeveelheid = aantal
            productSKU = product[1:4]
            order_id = order_id

        productinfo = Productinfo.objects.filter(productcode=productSKU).first()
        gang_id = productinfo.gang_id
        verpakkingmogelijkheid_id = productinfo.verpakkingscombinatie_id
        # TODO: als verpakkingmogelijk = 0, niet naar pickitems
        verpakkingsmogelijkheden = VerpakkingsCombinaties.objects.filter(
            verpakkingsmogelijkheid_id=verpakkingmogelijkheid_id)
        try:
            verpakkingsaantallen = verpakkingsmogelijkheden.get(
                bestelde_hoeveelheid=bestelde_hoeveelheid).verpakkingscombinatie
            for verpakking in verpakkingsaantallen:
                if verpakking != ',':
                    productID = str(gang_id) + productSKU + verpakking
                    try:
                        product_to_pick = Productinfo.objects.get(productID=productID)
                        PickItems.objects.create(omschrijving=product_to_pick.picknaam, hoeveelheid=1,
                                                 pick_order=PickOrders.objects.get(order_id=order_id),
                                                 product=product_to_pick)
                    except ObjectDoesNotExist:
                        print('Geen product gevonden Productinfo voor: ', productinfo.productnaam, productID)
        except ObjectDoesNotExist:
            print(
                "Productverpakking niet aanwezig in Verpakkings combinaties. Controleer database, ook 0 moet ingevuld worden",
                productinfo.productnaam)

    def make_product_extras(self, pickorderlines):
        print('MAKE PRODUCT EXTRAS')
        product_extras_dict = {}
        for product in pickorderlines:
            productextras = Productextra.objects.filter(productnaam__productcode=product.productSKU)
            for productextra in productextras:
                if productextra.extra_productnaam_id in product_extras_dict:
                    product_extras_dict[productextra.extra_productnaam_id] += product.aantal
                else:
                    product_extras_dict[productextra.extra_productnaam_id] = product.aantal
        order_id = pickorderlines[0].order_id
        for key, value in product_extras_dict.items():
            self.make_picks(key, value, order_id)


    def make_order_extras(self, order):
        print('MAKE ORDER EXTRAS')
        orderextras = Orderextra.objects.all()
        for orderextra in orderextras:
            productID = orderextra.productnaam_id
            productinfo = Productinfo.objects.filter(productID=productID).first()

            PickItems.objects.create(omschrijving=productinfo.picknaam, hoeveelheid=1,
                                     pick_order=PickOrders.objects.get(order_id=order.id),
                                     product=productinfo)

    def optimize_picks(self):
        for pickorder in PickOrders.objects.all():
            self.pickorderlines = PickItems.objects.filter(pick_order_id=pickorder)
            for product in self.pickorderlines:
                occurences = self.pickorderlines.filter(product_id=product.product_id).count()
                if occurences > 1:  # zelfde product, samenvoegen en 2e instance verwijderen uit db en for loop
                    double_picks = self.pickorderlines.filter(product_id=product.product_id)
                    omschrijving = double_picks.first().omschrijving
                    pick_order_id = double_picks.first().pick_order_id
                    product_id = double_picks.first().product_id
                    new_amount = double_picks.aggregate(Sum('hoeveelheid')).get('hoeveelheid__sum')
                    PickItems.objects.filter(pick_order_id=pick_order_id, product_id=product_id).delete()
                    PickItems.objects.create(omschrijving=omschrijving, hoeveelheid=new_amount,
                                             pick_order_id=pick_order_id, product_id=product_id)

    def calculate_variables(self):
        print('Calculate variables')
        # aantal orders
        aantal_orders = Orders.objects.all().count()
        AlgemeneInformatie.objects.filter(naam='aantalOrders').delete()
        AlgemeneInformatie.objects.create(naam='aantalOrders', waarde=aantal_orders)
        # aantal hoofdgerechten
        hoofdgerechten = Productinfo.objects.filter(gang_id__in=[4])
        # hoofdgerechten_array = list(hoofdgerechten.values_list('productcode', flat=True))
        hoofdgerechten_array = []
        for hoofdgerecht in hoofdgerechten:
            hoofdgerechten_array.append(int(hoofdgerecht.productcode))
        aantal_hoofdgerechten = Orderline.objects.filter(productSKU__in=hoofdgerechten_array).aggregate(Sum('aantal'))
        # aantal brunch
        brunches = Productinfo.objects.filter(productcode__in=[700, 701])
        brunch_array = []
        for brunch in brunches:
            brunch_array.append(brunch.productcode)
        aantal_brunch = Orderline.objects.filter(productSKU__in=brunch_array).aggregate(Sum('aantal'))
        # aantal gourmet
        gourmets = Productinfo.objects.filter(productcode__in=[750])
        gourmet_array = []
        for gourmet in gourmets:
            gourmet_array.append(gourmet.productcode)
        aantal_gourmets = Orderline.objects.filter(productSKU__in=gourmet_array).aggregate(Sum('aantal'))

        AlgemeneInformatie.objects.filter(naam='aantalHoofdgerechten').delete()
        AlgemeneInformatie.objects.filter(naam='aantalBrunch').delete()
        AlgemeneInformatie.objects.filter(naam='aantalGourmet').delete()
        try:
            AlgemeneInformatie.objects.create(naam='aantalHoofdgerechten',
                                              waarde=aantal_hoofdgerechten.get('aantal__sum'))
        except IntegrityError:
            AlgemeneInformatie.objects.create(naam='aantalHoofdgerechten', waarde=0)
        try:
            AlgemeneInformatie.objects.create(naam='aantalBrunch',
                                              waarde=aantal_brunch.get('aantal__sum'))
        except IntegrityError:
            AlgemeneInformatie.objects.create(naam='aantalBrunch', waarde=0)
        try:
            AlgemeneInformatie.objects.create(naam='aantalGourmet',
                                              waarde=aantal_gourmets.get('aantal__sum'))
        except IntegrityError:
            AlgemeneInformatie.objects.create(naam='aantalGourmet', waarde=0)

        AlgemeneInformatie.objects.filter(naam='status').delete()
        AlgemeneInformatie.objects.create(naam='status', waarde=100)
