from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count

from hefs.models import Orders, PickOrders, Orderline, PickItems, Productextra, Productinfo, \
    VerpakkingsCombinaties, Orderextra


class CalculateOrders():
    def __init__(self):
        print('CALCULATE ORDERS')
        PickOrders.objects.all().delete()
        PickItems.objects.all().delete()
        self.make_pickfile()
        # self.make_veh()

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
        else: #if it is a productextra
            bestelde_hoeveelheid = aantal
            productSKU = product.productcode
            order_id = order_id

        productinfo = Productinfo.objects.filter(productcode=productSKU).first()
        gang_id = productinfo.gang_id
        verpakkingmogelijkheid_id = productinfo.verpakkingscombinatie_id
        verpakkingsmogelijkheden = VerpakkingsCombinaties.objects.filter(verpakkingsmogelijkheid_id=verpakkingmogelijkheid_id)
        try:
            verpakkingsaantallen = verpakkingsmogelijkheden.get(bestelde_hoeveelheid=bestelde_hoeveelheid).verpakkingscombinatie
            for verpakking in verpakkingsaantallen:
                if verpakking != ',':
                    productID = str(gang_id) + productSKU + verpakking
                    try:
                        product_to_pick = Productinfo.objects.get(productID=productID)
                        PickItems.objects.create(omschrijving=productinfo.picknaam, hoeveelheid=1,
                                                 pick_order=PickOrders.objects.get(order_id=order_id),
                                                 product=product_to_pick)
                    except ObjectDoesNotExist:
                        # TODO: User feedback
                        print('Geen product gevonden Productinfo voor: ', productinfo.productnaam, productID)
        except ObjectDoesNotExist:
            #TODO: User feedback
            print("Productverpakking niet aanwezig in Verpakkings combinaties. Controleer database, ook 0 moet ingevuld worden")



    def make_product_extras(self, product):
        #TODO: als 1x brunch fixen en 1x brunch dasher -> samenvoegen en dan pas picks maken
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

    def make_veh(self):
        print('MAKE VEH')
        self.veh = PickItems.objects.select_related('pick_order__order').values_list('product_id',
            'pick_order__order__afleverdatum').annotate(totaal=Count('hoeveelheid'))

        return self.veh