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
                self.make_product_extras(product)

    def make_picks(self, product, aantal, order_id):
        if aantal == 'Geen productextra':
            bestelde_hoeveelheid = product.aantal
            productSKU = product.productSKU
            order_id = product.order_id
        else:  # if it is a productextra
            bestelde_hoeveelheid = aantal
            productSKU = product.productcode
            order_id = order_id

        productinfo = Productinfo.objects.filter(productcode=productSKU).first()
        gang_id = productinfo.gang_id
        verpakkingmogelijkheid_id = productinfo.verpakkingscombinatie_id
        #TODO: als verpakkingmogelijk = 0, niet naar pickitems
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
                        print("Pickitem gecreerd")
                    except ObjectDoesNotExist:
                        # TODO: User feedback
                        print('Geen product gevonden Productinfo voor: ', productinfo.productnaam, productID)
        except ObjectDoesNotExist:
            # TODO: User feedback
            print("Productverpakking niet aanwezig in Verpakkings combinaties. Controleer database, ook 0 moet ingevuld worden", productinfo.productnaam)

    def make_product_extras(self, product):
        print('MAKE PRODUCT EXTRAS')
        productextras = Productextra.objects.filter(productnaam__productcode=product.productSKU)
        aantal = product.aantal
        order_id = product.order_id
        for productextra in productextras:
            extra_product = productextra.extra_productnaam
            self.make_picks(extra_product, aantal, order_id)

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
                if occurences > 1:  #zelfde product, samenvoegen en 2e instance verwijderen uit db en for loop
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
        hoofdgerechten = Productinfo.objects.filter(gang_id__in=[5, 7])
        hoofdgerechten_array = []
        for hoofdgerecht in hoofdgerechten:
            hoofdgerechten_array.append(hoofdgerecht.productcode)
        aantal_hoofdgerechten = Orderline.objects.filter(productSKU__in=hoofdgerechten_array).aggregate(Sum('aantal'))
        AlgemeneInformatie.objects.filter(naam='aantalHoofdgerechten').delete()
        try:
            AlgemeneInformatie.objects.create(naam='aantalHoofdgerechten',
                                              waarde=aantal_hoofdgerechten.get('aantal__sum'))
        except IntegrityError:
            AlgemeneInformatie.objects.create(naam='aantalHoofdgerechten', waarde=0)
