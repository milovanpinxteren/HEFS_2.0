from django.db.models import Sum

from hefs.models import PercentueleKosten, VasteKosten, VariableKosten, ApiUrls, Orders, AlgemeneInformatie


class FinanceCalculator():

    def calculate_profit_table(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs
        #omzet brunch
        brunch_orders = Orders.objects.filter(organisatieID__in=organisations_to_show, orderline__productSKU__in=[700, 701])
        sum_brunch_incl_btw = brunch_orders.aggregate(total_orderprijs=Sum('orderprijs'))
        sum_brunch_incl_btw = float(sum_brunch_incl_btw['total_orderprijs'])
        sum_brunch_ex_btw = float(sum_brunch_incl_btw) / 1.09

        #omzet gourmet

        # omzet diners
        diner_orders = Orders.objects.exclude(organisatieID__in=organisations_to_show, orderline__productSKU__in=[700, 701, 750, 751])
        sum_diner_incl_btw = diner_orders.aggregate(total_orderprijs=Sum('orderprijs'))
        sum_diner_incl_btw = float(sum_diner_incl_btw['total_orderprijs'])
        sum_diner_ex_btw = float(sum_diner_incl_btw) / 1.09

        sum_verzendkosten_incl_btw = float(Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(
            Sum('verzendkosten')).get('verzendkosten__sum'))
        sum_verzendkosten_ex_btw = float(sum_verzendkosten_incl_btw) / 1.09
        total_incl_btw = sum_brunch_incl_btw + sum_diner_incl_btw + sum_verzendkosten_incl_btw
        total_ex_btw = sum_brunch_ex_btw + sum_diner_ex_btw + sum_verzendkosten_ex_btw

        profit_table = [] #omschrijving, ex btw, incl btw

        profit_table.append(['Omzet diners', sum_diner_ex_btw, sum_diner_incl_btw])
        profit_table.append(['Omzet brunch', sum_brunch_ex_btw, sum_brunch_incl_btw])
        profit_table.append(['Omzet verzendkosten', sum_verzendkosten_ex_btw, sum_verzendkosten_incl_btw])
        profit_table.append(['Omzet Totaal', total_ex_btw, total_incl_btw])
        return profit_table, total_ex_btw, total_incl_btw



    def calculate_costs_table(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs
        totale_inkomsten = Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(
            Sum('orderprijs')).get('orderprijs__sum')
        totale_verzendkosten = Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(
            Sum('verzendkosten')).get('verzendkosten__sum')
        try:
            inkomsten_zonder_verzendkosten = float(totale_inkomsten) - float(totale_verzendkosten)
            inkomsten_zonder_verzendkosten_ex_btw = inkomsten_zonder_verzendkosten / 1.09
        except TypeError:
            inkomsten_zonder_verzendkosten = 0
            inkomsten_zonder_verzendkosten_ex_btw = 0




        aantal_hoofdgerechten = AlgemeneInformatie.objects.get(naam='aantalHoofdgerechten').waarde
        aantal_orders = AlgemeneInformatie.objects.get(naam='aantalOrders').waarde


        costs_table_tuple = [] #name, percentage, kosten per eenheid, vermenigvuldiging, kosten ex, kosten incl
        percentual_costs = PercentueleKosten.objects.all()
        variable_costs = VariableKosten.objects.all()
        fixed_costs = VasteKosten.objects.all()


        for percentual_cost in percentual_costs:
            percentage = float(percentual_cost.percentage)
            amount_ex_btw = float((percentage / 100) * inkomsten_zonder_verzendkosten_ex_btw)
            amount_incl_btw = float((percentage / 100) * inkomsten_zonder_verzendkosten)
            costs_table_tuple.append([percentual_cost.kostennaam, percentage, '', '', amount_ex_btw, amount_incl_btw])

        for variable_cost in variable_costs:
            if variable_cost.vermenigvuldiging == 1: #per order
                amount_ex_btw = float(variable_cost.kosten_per_eenheid) * aantal_orders
                amount_incl_btw = amount_ex_btw * 1.09
                costs_table_tuple.append([variable_cost.kostennaam, '', float(variable_cost.kosten_per_eenheid), 'Per order', amount_ex_btw, amount_incl_btw])
            if variable_cost.vermenigvuldiging == 2: #per hoofdgerecht
                amount_ex_btw = float(variable_cost.kosten_per_eenheid) * aantal_hoofdgerechten
                amount_incl_btw = amount_ex_btw * 1.09
                costs_table_tuple.append([variable_cost.kostennaam, '', float(variable_cost.kosten_per_eenheid), 'Per hoofdgerecht', amount_ex_btw, amount_incl_btw])


        for fixed_cost in fixed_costs:
            costs_ex_btw = float(fixed_cost.kosten)
            costs_incl_btw = costs_ex_btw * 1.09
            costs_table_tuple.append([fixed_cost.kostennaam, '', '', '', costs_ex_btw, costs_incl_btw])

        total_costs_ex_btw = sum(x[4] for x in costs_table_tuple)
        total_costs_incl_btw = sum(x[5] for x in costs_table_tuple)
        costs_table_tuple.append(['Totaal', '', '', '', total_costs_ex_btw, total_costs_incl_btw])

        return costs_table_tuple, total_costs_ex_btw, total_costs_incl_btw

    def calculate_revenue_table(self, total_ex_btw, total_incl_btw, total_costs_ex_btw, total_costs_incl_btw):
        difference_ex_btw = total_ex_btw - total_costs_ex_btw
        difference_incl_btw = total_incl_btw - total_costs_incl_btw
        btw_difference = difference_incl_btw - difference_ex_btw

        revenue_table = []
        revenue_table.append(['Winst', difference_ex_btw, difference_incl_btw])
        revenue_table.append(['Verschil BTW', btw_difference, ''])
        return revenue_table

