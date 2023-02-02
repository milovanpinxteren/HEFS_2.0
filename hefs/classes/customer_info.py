import opy as opy
import pandas as pd
import pgeocode
import px as px

from hefs.models import Orders
import folium
from folium.plugins import HeatMap

class CustomerInfo():
    def __init__(self):
        print('customer info')
        self.customer_location_plot()

    def customer_location_plot(self):
        location_df = pd.DataFrame.from_records(Orders.objects.values_list('postcode'), columns=['Postal_code'])
        location_df['stripped_postal'] = location_df['Postal_code'].str.extract('(\d+)')


        nomi = pgeocode.Nominatim('nl')
        df_coordinates = nomi.query_postal_code(location_df['stripped_postal'].array)
        df_coordinates['weight'] = 1
        map_obj = folium.Map(location=[52.2130, 5.2794], zoom_start=7, tiles='Stamen Terrain', height=700, width=500)

        lats_longs = df_coordinates[['latitude', 'longitude', 'weight']].to_numpy()

        HeatMap(lats_longs).add_to(map_obj)
        return map_obj

    def orders_per_date_plot(self):
        pd.DataFrame.from_records(Orders.objects.values_list('postcode'), columns=['Postal_code'])

        fig = px.line(df_merged, x="Besteldatum", y="Totaal aantal personen", color='Jaar',
                      title="Aantal personen per datum")
        fig.update_xaxes(tickformat='%d-%m')
        fig.update_xaxes(nticks=25)
        fig.update_xaxes(gridcolor='lightgrey')
        fig.update_yaxes(gridcolor='lightgrey')
        fig.update_yaxes(range=[0, 8000])
        # fig.update_yaxes(range = ["28-8","18-12"])
        fig.update_yaxes(nticks=20)
        fig.update_layout(hoverlabel_bgcolor='green')
        fig.update_layout(plot_bgcolor='white')
        fig.add_shape(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1.0, y1=1.0,
                      line=dict(color="black", width=1))
        div_orders_graph = opy.plot(fig, auto_open=True, output_type='div')

