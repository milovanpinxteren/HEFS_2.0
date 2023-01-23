from hefs.models import Orders, PickOrders, Orderline, PickItems, Productextra


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
                self.make_product_extras(product)
                self.make_order_extras(product)

    def make_product_extras(self, product):
        print('MAKE PRODUCT EXTRAS')
        #Productextra.objects.filter(id=product.id) product.productSKU
        productextras = Productextra.objects.filter(productnaam__productcode=product.productSKU)
        print('extras zijn', productextras)
        for productextra in productextras:


    def make_order_extras(self, product):
        print('MAKE ORDER EXTRAS')

    def make_veh(self):
        print('MAKE VEH')