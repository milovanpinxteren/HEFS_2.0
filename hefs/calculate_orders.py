from django.core.exceptions import ObjectDoesNotExist

from hefs.models import Orders, PickOrders, Orderline, PickItems, Productextra, Productinfo, VerpakkingsMogelijkheden, VerpakkingsCombinaties


class CalculateOrders():
    def __init__(self):
        print('CALCULATE ORDERS')
        PickOrders.objects.all().delete()
        PickItems.objects.all().delete()
        self.make_pickfile()
        self.make_veh()

    def make_pickfile(self):
        print('MAKE PICKFILE')
        orders = Orders.objects.all()
        for order in orders:
            PickOrders.objects.create(order=order)

        for self.pickorder in PickOrders.objects.all():
            self.pickorderlines = Orderline.objects.filter(order=self.pickorder.order_id)
            for product in self.pickorderlines:
                self.make_picks(product, 'Geen productextra', 'Geen productextra')
                self.make_product_extras(product)
                # self.make_order_extras(product)

    def make_picks(self, product, aantal, order_id):

        try: #if pick is not a productextra
            bestelde_hoeveelheid = product.aantal
            productSKU = product.productSKU
            order_id = product.order_id
        except AttributeError: #if pick is a productextra
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
                        PickItems.objects.create(omschrijving=productinfo.productnaam, hoeveelheid=1,
                                                 pick_order=PickOrders.objects.get(order_id=order_id),
                                                 product=product_to_pick)
                    except ObjectDoesNotExist:
                        # TODO: User feedback
                        print('Geen product gevonden Productinfo voor: ', productinfo.productnaam, productID)
        except ObjectDoesNotExist:
            #TODO: User feedback
            print("Productverpakking niet aanwezig in Verpakkings combinaties. Controleer database, ook 0 moet ingevuld worden")



    def make_product_extras(self, product):
        print('MAKE PRODUCT EXTRAS')
        productextras = Productextra.objects.filter(productnaam__productcode=product.productSKU)
        aantal = product.aantal
        order_id = product.order_id
        print('extras zijn', productextras)
        for productextra in productextras:
            extra_product = productextra.extra_productnaam
            self.make_picks(extra_product, aantal, order_id)


    def make_order_extras(self, product):
        print('MAKE ORDER EXTRAS')

    def make_veh(self):
        print('MAKE VEH')