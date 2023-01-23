from hefs.models import NewOrders, Orders, Orderline


class AddOrders():
    def __init__(self):
        self.validate_orders()
        self.add_to_orderfile()
        self.check_orders()

    def validate_orders(self):
        print('VALIDEER ORDERS')
        #Optional

    def add_to_orderfile(self):
        print('ADD TO ORDERFILE')
        #TODO change values to values_list -> flat=True
        self.unique_conversieIDS = NewOrders.objects.values('conversieID').distinct()
        for conversieID in self.unique_conversieIDS:
            neworderlines = NewOrders.objects.filter(conversieID=conversieID['conversieID'])
            neworder_first = neworderlines.first()
            existing_order = Orders.objects.filter(conversieID=neworder_first.conversieID)
            if existing_order:
                print('Order al aanwezig in Orders model')
                # TODO: give feedback to user
            else:
                Orders.objects.create(conversieID=neworder_first.conversieID,
                                      besteldatum=neworder_first.besteldatum,
                                      afleverdatum=neworder_first.afleverdatum,
                                      aflevertijd=neworder_first.aflevertijd,
                                      verzendkosten=neworder_first.verzendkosten,
                                      korting=neworder_first.korting,
                                      orderprijs=neworder_first.orderprijs,
                                      organisatieID=neworder_first.organisatieID,
                                      organisatienaam=neworder_first.organisatienaam,
                                      voornaam=neworder_first.voornaam,
                                      achternaam=neworder_first.achternaam,
                                      tussenvoegsel=neworder_first.tussenvoegsel,
                                      emailadres=neworder_first.emailadres,
                                      telefoonnummer=neworder_first.telefoonnummer,
                                      straatnaam=neworder_first.straatnaam,
                                      huisnummer=neworder_first.huisnummer,
                                      postcode=neworder_first.postcode,
                                      plaats=neworder_first.plaats,
                                      land=neworder_first.land)
            for neworderline in neworderlines:
                order = Orders.objects.get(conversieID=neworderline.conversieID)
                existing_order = Orderline.objects.filter(order=order, product=neworderline.product,
                                                          productSKU=neworderline.productSKU,
                                                          aantal=neworderline.aantal)
                if existing_order:
                    print('Orderline al aanwezig in Orderline model')
                    # TODO: give feedback to user
                else:
                    Orderline.objects.create(order=order,
                                             product=neworderline.product,
                                             productSKU=neworderline.productSKU,
                                             aantal=neworderline.aantal)

    def check_orders(self):
        print('Check orders, en verwijder newOrders')
        #TODO check if all neworders are in orders and orderline (miss overdreven)

        # NewOrders.objects.all().delete()


