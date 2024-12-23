from datetime import datetime

from hefs.classes.pickbonnen import Pickbonnen
from hefs.models import Orders, PickOrders, PickItems, AlgemeneInformatie, Stop

import qrcode as qrcode


class PickbonnenGenerator:
    def __init__(self, begindatum, einddatum, conversieID, routenr):
        self.get_data(begindatum, einddatum, conversieID, routenr)

    def get_data(self, begindatum, einddatum, conversieID, routenr):
        ordersqueryset = Orders.objects.all()
        if begindatum != '' and einddatum != '' and routenr == '':
            begindate = datetime.strptime(begindatum, "%m/%d/%Y")
            enddate = datetime.strptime(einddatum, "%m/%d/%Y")
            ordersqueryset = ordersqueryset.filter(afleverdatum__range=(begindate, enddate)).order_by('stop__route__name', 'stop__sequence_number')
        elif begindatum != '' and einddatum != '' and routenr != '':
            begindate = datetime.strptime(begindatum, "%m/%d/%Y")
            enddate = datetime.strptime(einddatum, "%m/%d/%Y")
            ordersqueryset = ordersqueryset.filter(afleverdatum__range=(begindate, enddate)).filter(stop__route__name=routenr).order_by('stop__route__name', 'stop__sequence_number')
        elif conversieID != '':
            ordersqueryset = ordersqueryset.filter(conversieID=conversieID)
        elif begindatum == '' and einddatum == '' and conversieID == '' and routenr == '':
            pass
        pickbonnen = Pickbonnen()
        for order in ordersqueryset:
            naw = []
            try:
                route_name = Stop.objects.get(order=order).route.name
            except Stop.DoesNotExist:
                route_name = order.verzendoptie.verzendoptie  # Or handle the missing stop as needed
            except Stop.MultipleObjectsReturned:
                route_name = "Multiple Stops Found"  # Or handle appropriately

            if order.huisnummer != None:
                naw.extend(
                    [order.conversieID, order.voornaam, order.achternaam, order.straatnaam, order.huisnummer, order.plaats, order.postcode, order.afleverdatum, route_name])
            else:
                naw.extend(
                    [order.conversieID, order.voornaam, order.achternaam, order.straatnaam, '', order.plaats, order.postcode, order.afleverdatum, route_name])
            pickbonnen.add_page()
            pickbonnen.naw_function(naw)
            try:
                pick_order = PickOrders.objects.get(order=order)
                pickqueryset = PickItems.objects.filter(pick_order=pick_order).order_by('product__pickvolgorde')
            except PickOrders.DoesNotExist:
                print('pickorder does not exist', order.conversieID)
                pickqueryset = []
            pickcount = 0
            qr_text = str(order.conversieID) + '\n'
            for pick in pickqueryset:
                if pick.product.verpakkingscombinatie_id != 6:
                    pickbonnen.pick_function(pick, pickcount, order.conversieID)
                    pickcount += 1
                    qr_text += str(int(pick.hoeveelheid)) + '\t' + str(pick.product_id) + '\n'
            if order.huisnummer != None:
                naw_qr_text = "[addr]" + '\n' + str(order.conversieID) + '   ' + 'Route ' + str(route_name) + '\n' + str(order.straatnaam) + ' ' + str(order.huisnummer) + '\n' + str(order.postcode) + ' ' + str(order.plaats) + '\n' + str(order.afleverdatum)
            else:
                naw_qr_text = "[addr]" + '\n' + str(order.conversieID) + '   ' + 'Route ' + str(route_name) + '\n' + str(order.straatnaam) + '\n' + str(order.postcode) + ' ' + str(order.plaats) + '\n' + str(order.afleverdatum)

            naw_qr_code = qrcode.make(naw_qr_text)
            naw_qr_img = naw_qr_code.get_image()

            pick_qr_code = qrcode.make(qr_text)
            pick_qr_img = pick_qr_code.get_image()
            pickbonnen.qr_codecell(pick_qr_img)
            pickbonnen.klant_qr_cell(naw_qr_img)
        pickbonnen.output('pickbonnen.pdf', "rb")
        AlgemeneInformatie.objects.filter(naam='status').delete()
        AlgemeneInformatie.objects.create(naam='status', waarde=100)
