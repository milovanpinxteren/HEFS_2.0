from hefs.models import Orders


class PickbonnenGenerator:
    def __init__(self, begindatum, einddatum, conversieID, routenr):
        print(begindatum, einddatum, conversieID)
        self.get_data(begindatum, einddatum, conversieID, routenr)


    def get_data(self, begindatum, einddatum, conversieID, routenr):
        print('asdf')
        ordersqueryset = Orders.objects.all()

        if begindatum != '' and einddatum != '' and routenr == '':
            print(begindatum, einddatum)

            # ordersqueryset = ordersqueryset.filter(Q())
        elif begindatum != '' and einddatum == '' and routenr == '':
            print(begindatum, einddatum)
        elif conversieID != '':
            print(conversieID)
        if begindatum != '' and einddatum != '' and routenr != '':
            print(routenr)

        #nodig:
            #order_ids
        # def klantcell -> voor orderid
        # def pickcell -> voor pickitems op van het orderid