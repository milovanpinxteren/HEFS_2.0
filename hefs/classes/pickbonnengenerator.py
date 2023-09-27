from datetime import datetime

import qrcode as qrcode

from hefs.classes.pickbonnen import Pickbonnen
from hefs.models import Orders, PickOrders, PickItems


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
                [order.conversieID, order.voornaam, order.achternaam, order.straatnaam, order.huisnummer, order.plaats, order.postcode, order.afleverdatum])
            # TODO: for label: "[addr] '\n' conversieID '\n' adres '\n' plaats '\n' postcode '\n' voornaam '\n' achternaam
            pickbonnen.add_page()
            pickbonnen.naw_function(naw)
            pick_order = PickOrders.objects.get(order=order)
            pickqueryset = PickItems.objects.filter(pick_order=pick_order).order_by('product__pickvolgorde')
            pickcount = 0
            qr_text = str(order.conversieID) + '\n'
            for pick in pickqueryset:
                if pick.product.verpakkingscombinatie_id != 6:
                    pickbonnen.pick_function(pick, pickcount, order.conversieID)
                    pickcount += 1
                    qr_text += str(pick.hoeveelheid) + '\t' + str(pick.product_id) + '\n'
            print(qr_text)
            if order.huisnummer != None:
                naw_qr_text = "[addr]" + '\n' + str(order.conversieID) + '\n' + str(order.straatnaam) + str(order.huisnummer) + '\n' + str(order.plaats) + '\n' + str(order.postcode) + '\n' + str(order.voornaam) + '\n' + str(order.achternaam) + '\n' + str(order.afleverdatum)
            else:
                naw_qr_text = "[addr]" + '\n' + str(order.conversieID) + '\n' + str(order.straatnaam) + '\n' + str(order.plaats) + '\n' + str(order.postcode) + '\n' + str(order.voornaam) + '\n' + str(order.achternaam) + '\n' + str(order.afleverdatum)

            naw_qr_code = qrcode.make(naw_qr_text)
            naw_qr_img = naw_qr_code.get_image()

            pick_qr_code = qrcode.make(qr_text)
            pick_qr_img = pick_qr_code.get_image()
            pickbonnen.qr_codecell(pick_qr_img)
            pickbonnen.klant_qr_cell(naw_qr_img)
        pickbonnen.output('pickbonnen.pdf', "rb")
