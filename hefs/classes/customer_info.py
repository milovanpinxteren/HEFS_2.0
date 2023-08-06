# import opy as opy
import folium
import pandas as pd
import pgeocode
from django.db.models import Sum, Count, Avg
from folium.plugins import HeatMap
from plotly import express as px, offline as opy

from hefs.models import Orders, AlgemeneInformatie, ApiUrls, Customers, JSONData


class CustomerInfo():
    def orders_per_date_plot(self, userid):

        data_2020 = JSONData.objects.get(key='data_2020').value
        data_2021 = JSONData.objects.get(key='data_2021').value
        data_2022 = JSONData.objects.get(key='data_2022').value
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs
        df_dates = pd.DataFrame.from_records(
            Orders.objects.filter(organisatieID__in=organisations_to_show).values_list('besteldatum'),
            columns=['besteldatum'])
        df_dates['besteldatum'] = df_dates['besteldatum'].dt.strftime("%Y-%m-%d")
        df_dates['orders'] = 1
        df_dates_grouped = pd.DataFrame(df_dates.groupby(by=['besteldatum'])['orders'].sum())
        df_dates_grouped['Totaal aantal orders'] = df_dates_grouped['orders'].cumsum()
        df_dates_grouped['Jaar'] = 2023

        frames = [pd.DataFrame(data=data_2020), pd.DataFrame(data=data_2021), pd.DataFrame(data=data_2022),
                  df_dates_grouped]
        df_merged = pd.concat(frames)

        fig = px.line(df_merged, x="Besteldatum", y="Totaal aantal personen", color='Jaar',
                      title="Aantal personen per datum")
        fig.update_xaxes(tickformat='%d-%m')
        fig.update_xaxes(nticks=25)
        fig.update_xaxes(gridcolor='lightgrey')
        fig.update_yaxes(gridcolor='lightgrey')
        fig.update_yaxes(range=[0, 7000])
        fig.update_yaxes(nticks=20)
        fig.update_layout(hoverlabel_bgcolor='green')
        fig.update_layout(plot_bgcolor='white')
        fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1.0, y1=1.0,
                      line=dict(color="black", width=1))
        div_orders_graph = opy.plot(fig, auto_open=True, output_type='div')
        return div_orders_graph

    def important_numbers_table(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs

        totale_inkomsten = Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(
            Sum('orderprijs')).get('orderprijs__sum')
        totale_verzendkosten = Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(
            Sum('verzendkosten')).get('verzendkosten__sum')
        inkomsten_zonder_verzendkosten = totale_inkomsten - totale_verzendkosten

        aantal_hoofdgerechten = AlgemeneInformatie.objects.get(naam='aantalHoofdgerechten').waarde
        aantal_orders = AlgemeneInformatie.objects.get(naam='aantalOrders').waarde
        hoofdgerechten_per_order = aantal_hoofdgerechten / aantal_orders
        gem_omzet_per_order = inkomsten_zonder_verzendkosten / aantal_orders

        return aantal_hoofdgerechten, aantal_orders, hoofdgerechten_per_order, gem_omzet_per_order

    def returning_customers_overview(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs

        customers_2020 = Customers.objects.exclude(ordered_2020__isnull=True).count()
        customers_2021 = Customers.objects.exclude(ordered_2021__isnull=True).count()
        customers_2022 = Customers.objects.exclude(ordered_2022__isnull=True).count()

        returning_customers_2021 = Customers.objects.exclude(ordered_2020__isnull=True).exclude(ordered_2021__isnull=True).count()
        returning_customers_2022 = Customers.objects.exclude(ordered_2021__isnull=True).exclude(ordered_2022__isnull=True).count()
        returning_customers_2022 += Customers.objects.exclude(ordered_2020__isnull=True).exclude(ordered_2022__isnull=True).count()
        returning_customers_21_22 = Customers.objects.exclude(ordered_2020__isnull=True).exclude(ordered_2021__isnull=True).exclude(ordered_2022__isnull=True).count()

        # customers_2023 = Orders.objects.filter(organisatieID__in=organisations_to_show)
        values_model1 = Orders.objects.filter(organisatieID__in=organisations_to_show).values_list('emailadres', flat=True).distinct()
        values_model2 = Customers.objects.values_list('emailadres', flat=True).distinct()

        # Find the overlapping values
        returning_customers_2023 = len(set(values_model1) & set(values_model2))
        return customers_2020, customers_2021, customers_2022, returning_customers_2021, returning_customers_2022, returning_customers_21_22, returning_customers_2023

    def orders_worth_table(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs

        avg_orders_worth_2020 = 174.02307692307696
        avg_orders_worth_2021 = 172.8445392491467
        avg_orders_worth_2022 = 229.55841371918822
        avg_orders_worth_2023 = Orders.objects.filter(organisatieID__in=organisations_to_show).aggregate(Avg('orderprijs'))['orderprijs__avg']

        return avg_orders_worth_2020, avg_orders_worth_2021, avg_orders_worth_2022, avg_orders_worth_2023

    def dinner_type_comparison(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs

        distribution_2022 = JSONData.objects.get(key='distribution_2022').value
        aantal_hoofdgerechten = AlgemeneInformatie.objects.get(naam='aantalHoofdgerechten').waarde
        aantal_brunches = AlgemeneInformatie.objects.get(naam='aantalBrunch').waarde
        aantal_gourmets = AlgemeneInformatie.objects.get(naam='aantalGourmet').waarde
        percentage_brunch = float((aantal_brunches / aantal_hoofdgerechten) * 100)
        percentage_gourmet = float((aantal_gourmets / aantal_hoofdgerechten) * 100)

        distribution_2023 = {"aantal personen": aantal_hoofdgerechten, "aantal personen brunch": aantal_brunches,
                             "aantal personen gourmet": aantal_gourmets, "percentage brunch": percentage_brunch,
                             "percentage gourmet": percentage_gourmet}
        return distribution_2022, distribution_2023


    def prepare_view(self, userid):
        returning_customers_overview = self.returning_customers_overview(userid)
        orders_per_date_plot = self.orders_per_date_plot(userid)
        important_numbers = self.important_numbers_table(userid)
        orders_worth_table = self.orders_worth_table(userid)
        dinner_type_comparison = self.dinner_type_comparison(userid)
        context = {'returning_customers_overview': returning_customers_overview,
                   'orders_per_date_plot': orders_per_date_plot,
                   'aantal_hoofdgerechten': important_numbers[0], 'aantal_orders': important_numbers[1],
                   'hoofdgerechten_per_order': important_numbers[2], 'gem_omzet_per_order': important_numbers[3],
                   'customers_2020': returning_customers_overview[0], 'customers_2021': returning_customers_overview[1],
                   'customers_2022': returning_customers_overview[2], 'returning_customers_2021': returning_customers_overview[3],
                   'returning_customers_2022': returning_customers_overview[4],'returning_customers_21_22': returning_customers_overview[5],
                   'returning_customers_2023': returning_customers_overview[6], 'avg_orders_worth_2020': orders_worth_table[0],
                   'avg_orders_worth_2021': orders_worth_table[1], 'avg_orders_worth_2022': orders_worth_table[2],
                   'avg_orders_worth_2023': orders_worth_table[3], 'dinner_type_comparison': dinner_type_comparison}
        return context
