from django.db.models import Sum

from hefs.models import PercentueleKosten, VasteKosten, VariableKosten, ApiUrls, Orders, AlgemeneInformatie


class FinanceCalculator():
    def __init__(self, userid):
        self.calculate_profit(userid)
        self.calculate_costs()
        self.calculate_revenue()

    def calculate_profit(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs
        self.totale_inkomsten = Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(
            Sum('orderprijs')).get('orderprijs__sum')
        totale_verzendkosten = Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(
            Sum('verzendkosten')).get('verzendkosten__sum')
        self.inkomsten_zonder_verzendkosten = self.totale_inkomsten - totale_verzendkosten
        self.aantal_hoofdgerechten = AlgemeneInformatie.objects.get(naam='aantalHoofdgerechten').waarde
        self.aantal_orders = AlgemeneInformatie.objects.get(naam='aantalOrders').waarde
        return self.totale_inkomsten, self.inkomsten_zonder_verzendkosten, self.aantal_hoofdgerechten, self.aantal_orders


    def calculate_costs(self):
        percentual_costs_table = PercentueleKosten.objects.all()
        total_percentage = PercentueleKosten.objects.aggregate(Sum('percentage'))
        percentual_costs = self.inkomsten_zonder_verzendkosten * (total_percentage.get('percentage__sum') / 100)
        percentual_costs_incl_btw = float(percentual_costs) * 1.09

        fixed_costs = VasteKosten.objects.all()
        total_fixed_costs_dict = VasteKosten.objects.aggregate(Sum('kosten'))
        total_fixed_costs = total_fixed_costs_dict.get('kosten__sum')
        fixed_costs_incl_btw = float(total_fixed_costs) * 1.09

        variable_costs = VariableKosten.objects.all()
        costs_per_order_dict = VariableKosten.objects.filter(vermenigvuldiging=1).aggregate(Sum('kosten_per_eenheid'))
        total_costs_per_order = costs_per_order_dict.get('kosten_per_eenheid__sum')
        total_order_costs = total_costs_per_order * self.aantal_orders

        costs_per_hoofdgerecht_dict = VariableKosten.objects.filter(vermenigvuldiging=2).aggregate(Sum('kosten_per_eenheid'))
        total_costs_per_hoofdgerecht = costs_per_hoofdgerecht_dict.get('kosten_per_eenheid__sum')
        total_hoofdgerechten_costs = total_costs_per_hoofdgerecht * self.aantal_hoofdgerechten
        total_variable_costs = total_order_costs + total_hoofdgerechten_costs
        total_variable_costs_incl_btw = float(total_variable_costs) * 1.09

        total_costs = percentual_costs + total_fixed_costs + total_variable_costs
        total_costs_incl_btw = percentual_costs_incl_btw + fixed_costs_incl_btw + total_variable_costs_incl_btw

        return percentual_costs_table, fixed_costs, variable_costs, percentual_costs, percentual_costs_incl_btw, \
               total_fixed_costs, fixed_costs_incl_btw, total_variable_costs, total_variable_costs_incl_btw, \
               total_costs, total_costs_incl_btw

    def calculate_revenue(self):
        print('test')
