# import opy as opy
import folium
import pandas as pd
import pgeocode
from folium.plugins import HeatMap

from hefs.models import Orders, ApiUrls

class CustomerLocationPlot():
    def customer_location_plot(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs
        location_df = pd.DataFrame.from_records(
            Orders.objects.filter(organisatieID__in=organisations_to_show).values_list('postcode'),
            columns=['Postal_code'])
        location_df['stripped_postal'] = location_df['Postal_code'].str.extract('(\d+)')

        nomi = pgeocode.Nominatim('nl')
        df_coordinates = nomi.query_postal_code(location_df['stripped_postal'].array)
        df_coordinates['weight'] = 1
        map_obj = folium.Map(location=[52.2130, 5.2794], zoom_start=7, tiles='cartodb positron')

        lats_longs = df_coordinates[['latitude', 'longitude', 'weight']].dropna().to_numpy()

        HeatMap(lats_longs).add_to(map_obj)
        return map_obj

