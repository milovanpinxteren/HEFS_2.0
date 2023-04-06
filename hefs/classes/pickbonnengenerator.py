import qrcode as qrcode

from hefs.classes.pickbonnen import Pickbonnen
from hefs.models import Orders, PickOrders, PickItems
from datetime import datetime


class PickbonnenGenerator:
    def __init__(self, begindatum, einddatum, conversieID, routenr):
        self.get_data(begindatum, einddatum, conversieID, routenr)

    def get_data(self, begindatum, einddatum, conversieID, routenr):
        ordersqueryset = Orders.objects.all()
        if begindatum != '' and einddatum != '' and routenr == '':
            begindate = datetime.strptime(begindatum, "%m/%d/%Y")
            enddate = datetime.strptime(einddatum, "%m/%d/%Y")
            ordersqueryset = ordersqueryset.filter(afleverdatum__range=(begindate, enddate))
        elif begindatum != '' and einddatum != '' and routenr != '':
            pass
            # TODO: routenr implementeren
        elif conversieID != '':
            ordersqueryset = ordersqueryset.filter(conversieID=conversieID)
        elif begindatum == '' and einddatum == '' and conversieID == '' and routenr == '':
            pass
        pickbonnen = Pickbonnen()
        for order in ordersqueryset:
            naw = []
            naw.extend(
                [order.conversieID, order.voornaam, order.achternaam, order.postcode, order.plaats, order.emailadres,
                 order.telefoonnummer, order.afleverdatum])

            pickbonnen.add_page()
            pickbonnen.naw_function(naw)
            pick_order = PickOrders.objects.get(order=order)
            pickqueryset = PickItems.objects.filter(pick_order=pick_order).order_by('product__pickvolgorde')
            pickcount = 0
            qr_text = str(order.conversieID) + ' \n '
            for pick in pickqueryset:
                if pick.product.verpakkingscombinatie_id != 6:
                    pickbonnen.pick_function(pick, pickcount, order.conversieID)
                    pickcount += 1
                    # pick.hoeveelheid
                    # pick.product_id
                    qr_text += '\t' + str(pick.hoeveelheid) + ' \t' + str(pick.product_id) + ' \n'
            print(qr_text)
            qr_code = qrcode.make(qr_text)
            img = qr_code.get_image()
            pickbonnen.qr_codecell(img)
        pickbonnen.output('pickbonnen.pdf', "rb")


