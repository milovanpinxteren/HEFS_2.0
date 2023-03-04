# import opy as opy
import pandas as pd
import pgeocode
from django.db.models import Sum
from plotly import express as px, offline as opy

from hefs.models import Orders, AlgemeneInformatie, ApiUrls
import folium
from folium.plugins import HeatMap

class CustomerInfo():
    def customer_location_plot(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs
        location_df = pd.DataFrame.from_records(Orders.objects.filter(organisatieID__in=organisations_to_show).values_list('postcode'), columns=['Postal_code'])
        location_df['stripped_postal'] = location_df['Postal_code'].str.extract('(\d+)')


        nomi = pgeocode.Nominatim('nl')
        df_coordinates = nomi.query_postal_code(location_df['stripped_postal'].array)
        df_coordinates['weight'] = 1
        map_obj = folium.Map(location=[52.2130, 5.2794], zoom_start=7, tiles='Stamen Terrain')

        lats_longs = df_coordinates[['latitude', 'longitude', 'weight']].to_numpy()

        HeatMap(lats_longs).add_to(map_obj)
        return map_obj

    def orders_per_date_plot(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs
        df_dates = pd.DataFrame.from_records(Orders.objects.filter(organisatieID__in=organisations_to_show).values_list('besteldatum'), columns=['besteldatum'])
        df_dates['besteldatum'] = df_dates['besteldatum'].dt.strftime("%Y-%m-%d")
        df_dates['orders'] = 1
        df_dates_grouped = pd.DataFrame(df_dates.groupby(by=['besteldatum'])['orders'].sum())
        df_dates_grouped['Totaal aantal orders'] = df_dates_grouped['orders'].cumsum()
        df_dates_grouped['Jaar'] = 2023

        fig = px.line(df_dates_grouped, x=df_dates_grouped.index, y="Totaal aantal orders", color='Jaar',
                      title="Aantal orders per datum")
        fig.update_xaxes(tickformat='%d-%m')
        fig.update_xaxes(nticks=25)
        fig.update_xaxes(gridcolor='lightgrey')
        fig.update_yaxes(gridcolor='lightgrey')
        fig.update_yaxes(range=[0, 20])
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

