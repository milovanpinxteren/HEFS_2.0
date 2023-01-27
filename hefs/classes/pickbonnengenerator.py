from hefs.classes.pickbonnen import Pickbonnen
from hefs.models import Orders
from datetime import datetime

class PickbonnenGenerator:
    def __init__(self, begindatum, einddatum, conversieID, routenr):
        print(begindatum, einddatum, conversieID)
        self.get_data(begindatum, einddatum, conversieID, routenr)


    def get_data(self, begindatum, einddatum, conversieID, routenr):
        ordersqueryset = Orders.objects.all()
        if begindatum != '' and einddatum != '' and routenr == '':
            begindate = datetime.strptime(begindatum, "%m/%d/%Y")
            enddate = datetime.strptime(einddatum, "%m/%d/%Y")
            ordersqueryset = ordersqueryset.filter(afleverdatum__range=(begindate, enddate))
        elif begindatum != '' and einddatum != '' and routenr != '':
            pass
            #TODO: routenr implementeren
        elif conversieID != '':
            ordersqueryset = ordersqueryset.filter(conversieID=conversieID)
        elif begindatum == '' and einddatum == '' and conversieID == '' and routenr == '':
            pass

        for order in ordersqueryset:
            naw = []
            naw.extend([order.conversieID, order.voornaam, order.achternaam, order.postcode, order.plaats, order.emailadres,
                       order.telefoonnummer, order.afleverdatum])
            pickbonnen = Pickbonnen()
            pickbonnen.pickbon_function(naw)

