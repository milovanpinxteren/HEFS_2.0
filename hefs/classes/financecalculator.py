from django.db.models import F, ExpressionWrapper, DecimalField, Sum

from hefs.models import PercentueleKosten, VasteKosten, VariableKosten, ApiUrls, Orders, AlgemeneInformatie, Orderline, \
    PickItems


class FinanceCalculator():

    def calculate_profit_table(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs
        # omzet brunch
        brunch_orders = Orders.objects.filter(organisatieID__in=organisations_to_show,
                                              orderline__productSKU__in=[700, 701])
        sum_brunch_incl_btw = brunch_orders.aggregate(total_orderprijs=Sum('orderprijs'))
        if sum_brunch_incl_btw['total_orderprijs'] == None:
            sum_brunch_incl_btw['total_orderprijs'] = 0
        self.sum_brunch_incl_btw = float(sum_brunch_incl_btw['total_orderprijs'])
        self.sum_brunch_ex_btw = float(self.sum_brunch_incl_btw) / 1.09

        # omzet diners
        diner_orders = Orders.objects.exclude(organisatieID__in=organisations_to_show,
                                              orderline__productSKU__in=[700, 701, 750, 751])
        sum_diner_incl_btw = diner_orders.aggregate(total_orderprijs=Sum('orderprijs'))
        self.sum_diner_incl_btw = float(sum_diner_incl_btw['total_orderprijs'])
        self.sum_diner_ex_btw = float(self.sum_diner_incl_btw) / 1.09

        sum_verzendkosten_incl_btw = float(Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(
            Sum('verzendkosten')).get('verzendkosten__sum'))
        sum_verzendkosten_ex_btw = float(sum_verzendkosten_incl_btw) / 1.09
        total_incl_btw = self.sum_brunch_incl_btw + self.sum_diner_incl_btw + sum_verzendkosten_incl_btw
        total_ex_btw = self.sum_brunch_ex_btw + self.sum_diner_ex_btw + sum_verzendkosten_ex_btw

        profit_table = []  # omschrijving, ex btw, incl btw

        profit_table.append(['Omzet diners', self.sum_diner_ex_btw, self.sum_diner_incl_btw])
        profit_table.append(['Omzet brunch', self.sum_brunch_ex_btw, self.sum_brunch_incl_btw])
        profit_table.append(['Omzet verzendkosten', sum_verzendkosten_ex_btw, sum_verzendkosten_incl_btw])
        profit_table.append(['Omzet Totaal', total_ex_btw, total_incl_btw])
        return profit_table, total_ex_btw, total_incl_btw

    def calculate_costs_table(self, userid):
        inkomsten_zonder_verzendkosten = self.sum_brunch_incl_btw + self.sum_diner_incl_btw
        inkomsten_zonder_verzendkosten_ex_btw = self.sum_brunch_ex_btw + self.sum_diner_ex_btw


        self.aantal_hoofdgerechten = AlgemeneInformatie.objects.get(naam='aantalHoofdgerechten').waarde
        self.aantal_brunch = AlgemeneInformatie.objects.get(naam='aantalBrunch').waarde
        self.aantal_orders = AlgemeneInformatie.objects.get(naam='aantalOrders').waarde

        costs_table_tuple = []  # name, percentage, kosten per eenheid, vermenigvuldiging, kosten ex, kosten incl
        percentual_costs = PercentueleKosten.objects.all()
        variable_costs = VariableKosten.objects.all()
        fixed_costs = VasteKosten.objects.all()

        try:
            total_bereidingskosten_diner_ex_btw = float(
                PickItems.objects.exclude(product__gang=7).annotate(
                    total_kosten=ExpressionWrapper(
                        F('product__bereidingskosten') * F('hoeveelheid'),
                        output_field=DecimalField(max_digits=8, decimal_places=2)
                    )
                ).aggregate(total_bereidingskosten=Sum('total_kosten'))['total_bereidingskosten'] or 0
            )

            total_bereidingskosten_diner_incl_btw = float(
                PickItems.objects.exclude(product__gang=7).annotate(
                    total_kosten=ExpressionWrapper(
                        F('product__bereidingskosten') * F('product__btw') * F('hoeveelheid'),
                        output_field=DecimalField(max_digits=8, decimal_places=2)
                    )
                ).aggregate(total_bereidingskosten=Sum('total_kosten'))['total_bereidingskosten'] or 0
            )

            total_bereidingskosten_brunch_ex_btw = float(
                PickItems.objects.filter(product__gang=7).annotate(
                    total_kosten=ExpressionWrapper(
                        F('product__bereidingskosten') * F('hoeveelheid'),
                        output_field=DecimalField(max_digits=8, decimal_places=2)
                    )
                ).aggregate(total_bereidingskosten=Sum('total_kosten'))['total_bereidingskosten'] or 0
            )

            total_bereidingskosten_brunch_incl_btw = float(
                PickItems.objects.filter(product__gang=7).annotate(
                    total_kosten=ExpressionWrapper(
                        F('product__bereidingskosten') * F('product__btw') * F('hoeveelheid'),
                        output_field=DecimalField(max_digits=8, decimal_places=2)
                    )
                ).aggregate(total_bereidingskosten=Sum('total_kosten'))['total_bereidingskosten'] or 0
            )

        except Exception as e:
            # If an error occurs, assign 0 to each variable
            total_bereidingskosten_diner_ex_btw = 0
            total_bereidingskosten_diner_incl_btw = 0
            total_bereidingskosten_brunch_ex_btw = 0
            total_bereidingskosten_brunch_incl_btw = 0
            # Optional: Log the exception for debugging purposes
            print(f"An error occurred: {e}")

        costs_table_tuple.append(
            ['bereidingskosten food', '', '', '', total_bereidingskosten_diner_ex_btw + total_bereidingskosten_brunch_ex_btw, total_bereidingskosten_diner_incl_btw + total_bereidingskosten_brunch_incl_btw])

        for percentual_cost in percentual_costs:
            percentage = float(percentual_cost.percentage)
            amount_ex_btw = float((percentage / 100) * inkomsten_zonder_verzendkosten_ex_btw)
            amount_incl_btw = float((percentage / 100) * inkomsten_zonder_verzendkosten)
            costs_table_tuple.append([percentual_cost.kostennaam, percentage, '', '', amount_ex_btw, amount_incl_btw])

        for variable_cost in variable_costs:
            if variable_cost.vermenigvuldiging == 1:  # per order
                amount_ex_btw = float(variable_cost.kosten_per_eenheid) * self.aantal_orders
                amount_incl_btw = amount_ex_btw * 1.09
                costs_table_tuple.append(
                    [variable_cost.kostennaam, '', float(variable_cost.kosten_per_eenheid), 'Per order', amount_ex_btw,
                     amount_incl_btw])
            if variable_cost.vermenigvuldiging == 2:  # per persoon (hoofdgerecht + brunch)
                amount_ex_btw = float(variable_cost.kosten_per_eenheid) * (self.aantal_hoofdgerechten + self.aantal_brunch)
                amount_incl_btw = amount_ex_btw * 1.09
                costs_table_tuple.append(
                    [variable_cost.kostennaam, '', float(variable_cost.kosten_per_eenheid), 'Per hoofdgerecht',
                     amount_ex_btw, amount_incl_btw])

        for fixed_cost in fixed_costs:
            costs_ex_btw = float(fixed_cost.kosten)
            costs_incl_btw = costs_ex_btw * 1.09
            costs_table_tuple.append([fixed_cost.kostennaam, '', '', 'Vaste kosten', costs_ex_btw, costs_incl_btw])

        self.total_costs_ex_btw = sum(x[4] for x in costs_table_tuple)
        self.total_costs_incl_btw = sum(x[5] for x in costs_table_tuple)
        costs_table_tuple.append(['Totaal', '', '', '', self.total_costs_ex_btw, self.total_costs_incl_btw])

        for cost in costs_table_tuple:
            cost[1] = float((cost[4] / inkomsten_zonder_verzendkosten_ex_btw) * 100)

        try:
            percentage_costs_dinner_ex_btw = float((total_bereidingskosten_diner_ex_btw / self.sum_diner_ex_btw) * 100)
            percentage_costs_brunch_ex_btw = float((total_bereidingskosten_brunch_ex_btw / self.sum_brunch_ex_btw) * 100)
        except Exception as e:
            percentage_costs_dinner_ex_btw = 0
            percentage_costs_brunch_ex_btw = 0

        costs_of_bereidingskosten_dict = {'Percentage kosten diner t.o.v. inkomsten diner': percentage_costs_dinner_ex_btw,
                                'Percentage kosten brunch t.o.v. inkomsten brunch': percentage_costs_brunch_ex_btw,
                                }
        return costs_table_tuple, self.total_costs_ex_btw, self.total_costs_incl_btw, costs_of_bereidingskosten_dict

    def calculate_revenue_table(self, total_ex_btw, total_incl_btw, total_costs_ex_btw, total_costs_incl_btw):
        difference_ex_btw = total_ex_btw - total_costs_ex_btw
        difference_incl_btw = total_incl_btw - total_costs_incl_btw

        income_ex_btw = self.sum_brunch_ex_btw + self.sum_diner_ex_btw
        income_minus_commission_ex_btw = income_ex_btw * 0.85  # income minus HaH commission, now hardcoded, maybe softcoding in future
        income_incl_btw = self.sum_brunch_incl_btw + self.sum_diner_incl_btw
        income_minus_commission_incl_btw = income_incl_btw * 0.85  # income minus HaH commission, now hardcoded, maybe softcoding in future

        btw_diff = (income_minus_commission_incl_btw - income_minus_commission_ex_btw) - (
                    self.total_costs_incl_btw - self.total_costs_ex_btw)

        revenue_table = []
        revenue_table.append(['Winst', difference_ex_btw])
        revenue_table.append(['Verschil BTW', btw_diff])
        return revenue_table

    def calculate_prognose_profit_table(self, profit_table):
        prognose_profit_table = []

        self.prognosegetal_diner = AlgemeneInformatie.objects.get(naam='prognosegetal_diner').waarde
        self.prognosegetal_brunch = AlgemeneInformatie.objects.get(naam='prognosegetal_brunch').waarde

        try:
            prognose_factor_diner = self.prognosegetal_diner / self.aantal_hoofdgerechten
            prognose_factor_brunch = self.prognosegetal_brunch / self.aantal_brunch
            prognose_factor_totaal = (self.prognosegetal_diner + self.prognosegetal_brunch) / (self.aantal_hoofdgerechten + self.aantal_brunch)
        except ZeroDivisionError:
            prognose_factor_diner = 0
            prognose_factor_brunch = 0
            prognose_factor_totaal = 0

        for row in profit_table:
            if 'diner' in row[0]:
                sum_diner_ex_btw = row[1] * prognose_factor_diner
                sum_diner_incl_btw = row[2] * prognose_factor_diner
                prognose_profit_table.append(['Omzet diners', sum_diner_ex_btw, sum_diner_incl_btw])
            elif 'brunch' in row[0]:
                sum_brunch_ex_btw = row[1] * prognose_factor_brunch
                sum_brunch_incl_btw = row[2] * prognose_factor_brunch
                prognose_profit_table.append(['Omzet brunch', sum_brunch_ex_btw, sum_brunch_incl_btw])
            elif 'verzendkosten' in row[0]:
                sum_shipping_ex_btw = row[1] * prognose_factor_totaal
                sum_shipping_incl_btw = row[2] * prognose_factor_totaal
                prognose_profit_table.append(['Omzet verzendkosten', sum_shipping_ex_btw, sum_shipping_incl_btw])
            elif 'Totaal' in row[0]:
                prognose_sum_total_ex_btw = row[1] * prognose_factor_totaal
                prognose_sum_total_incl_btw = row[2] * prognose_factor_totaal
                prognose_profit_table.append(['Omzet Totaal', prognose_sum_total_ex_btw, prognose_sum_total_incl_btw])

        self.prognose_ex_verzendk_ex_btw = prognose_sum_total_ex_btw - sum_shipping_ex_btw
        self.prognose_ex_verzendk_incl_btw = prognose_sum_total_incl_btw - sum_shipping_incl_btw
        return prognose_profit_table, prognose_sum_total_ex_btw, prognose_sum_total_incl_btw

    def calculate_prognose_costs_table(self, costs_table):

        try:
            prognose_factor_diner = self.prognosegetal_diner / self.aantal_hoofdgerechten
            prognose_factor_totaal = (self.prognosegetal_diner + self.prognosegetal_brunch) / (self.aantal_hoofdgerechten + self.aantal_brunch)
        except ZeroDivisionError:
            prognose_factor_diner = 0
            prognose_factor_totaal = 0

        prognose_cost_table = []
        for cost in costs_table:
            if cost[2] == '' and cost[3] == '' and cost[0] != 'Totaal' and cost[0]:
                cost_ex_btw = cost[4] * prognose_factor_totaal
                cost_incl_btw = cost_ex_btw * 1.09
                prognose_cost_table.append([cost[0], '', '', '', cost_ex_btw, cost_incl_btw])
            elif cost[2] != '' and cost[3] == 'Per order':
                cost_ex_btw = cost[4] * prognose_factor_totaal
                cost_incl_btw = cost_ex_btw * 1.09
                prognose_cost_table.append([cost[0], '', '', '', cost_ex_btw, cost_incl_btw])
            elif cost[2] != '' and cost[3] == 'Per hoofdgerecht':
                cost_ex_btw = cost[4] * prognose_factor_totaal
                cost_incl_btw = cost_ex_btw * 1.09
                prognose_cost_table.append([cost[0], '', '', '', cost_ex_btw, cost_incl_btw])
            elif cost[3] == 'Vaste kosten':
                prognose_cost_table.append([cost[0], cost[1], cost[2], cost[3], cost[4], cost[5]])

        self.prognose_total_costs_ex_btw = sum(x[4] for x in prognose_cost_table)
        self.prognose_total_costs_incl_btw = sum(x[5] for x in prognose_cost_table)
        prognose_cost_table.append(['Totaal', '', '', '', self.prognose_total_costs_ex_btw, self.prognose_total_costs_incl_btw])

        for cost in prognose_cost_table:
            exists_in_database = PercentueleKosten.objects.filter(kostennaam=cost[0])
            if not exists_in_database:
                try:
                    cost[1] = (cost[4] / self.prognose_ex_verzendk_ex_btw) * 100
                except ZeroDivisionError:
                    cost[1] = 0
            elif exists_in_database:
                percentage = float(exists_in_database[0].percentage) / 100
                cost[1] = percentage * 100
                cost[4] = self.prognose_ex_verzendk_ex_btw * percentage
                cost[5] = self.prognose_ex_verzendk_ex_btw * percentage * 1.21

        return prognose_cost_table, self.prognose_total_costs_ex_btw, self.prognose_total_costs_incl_btw

    def calculate_prognose_revenue_table(self, prognose_sum_total_ex_btw, prognose_sum_total_incl_btw,
                                         prognose_total_costs_ex_btw, prognose_total_costs_incl_btw):
        difference_ex_btw = prognose_sum_total_ex_btw - prognose_total_costs_ex_btw
        difference_incl_btw = prognose_sum_total_incl_btw - prognose_total_costs_incl_btw


        income_ex_btw = self.prognose_ex_verzendk_ex_btw
        income_minus_commission_ex_btw = income_ex_btw * 0.85  # income minus HaH commission, now hardcoded, maybe softcoding in future
        income_incl_btw = self.prognose_ex_verzendk_incl_btw
        income_minus_commission_incl_btw = income_incl_btw * 0.85  # income minus HaH commission, now hardcoded, maybe softcoding in future

        btw_diff = (income_minus_commission_incl_btw - income_minus_commission_ex_btw) - (
                self.prognose_total_costs_incl_btw - self.prognose_total_costs_ex_btw)

        prognose_revenue_table = []
        prognose_revenue_table.append(['Winst', difference_ex_btw, difference_incl_btw])
        prognose_revenue_table.append(['Verschil BTW', btw_diff, ''])
        return prognose_revenue_table
