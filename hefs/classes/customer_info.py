# import opy as opy
import folium
import pandas as pd
import pgeocode
from django.db.models import Sum, Count, Avg
from folium.plugins import HeatMap
from plotly import express as px, offline as opy

from hefs.models import Orders, AlgemeneInformatie, ApiUrls, Customers


class CustomerInfo():
    def customer_location_plot(self, userid):
        organisations_to_show = ApiUrls.objects.get(user_id=userid).organisatieIDs
        location_df = pd.DataFrame.from_records(
            Orders.objects.filter(organisatieID__in=organisations_to_show).values_list('postcode'),
            columns=['Postal_code'])
        location_df['stripped_postal'] = location_df['Postal_code'].str.extract('(\d+)')

        nomi = pgeocode.Nominatim('nl')
        df_coordinates = nomi.query_postal_code(location_df['stripped_postal'].array)
        df_coordinates['weight'] = 1
        map_obj = folium.Map(location=[52.2130, 5.2794], zoom_start=7, tiles='Stamen Terrain')

        lats_longs = df_coordinates[['latitude', 'longitude', 'weight']].to_numpy()

        HeatMap(lats_longs).add_to(map_obj)
        return map_obj

    def orders_per_date_plot(self, userid):
        data_2020 = {
            "Besteldatum": {"0": "2023-10-02", "1": "2023-10-17", "2": "2023-10-25", "3": "2023-10-28",
                            "4": "2023-10-30",
                            "5": "2023-11-01", "6": "2023-11-04", "7": "2023-11-09", "8": "2023-11-10",
                            "9": "2023-11-12",
                            "10": "2023-11-13", "11": "2023-11-14", "12": "2023-11-15", "13": "2023-11-18",
                            "14": "2023-11-19", "15": "2023-11-21", "16": "2023-11-22", "17": "2023-11-23",
                            "18": "2023-11-24", "19": "2023-11-25", "20": "2023-11-26", "21": "2023-11-27",
                            "22": "2023-11-29", "23": "2023-11-30", "24": "2023-12-01", "25": "2023-12-02",
                            "26": "2023-12-03", "27": "2023-12-04", "28": "2023-12-05", "29": "2023-12-06",
                            "30": "2023-12-07", "31": "2023-12-08", "32": "2023-12-09", "33": "2023-12-10",
                            "34": "2023-12-11", "35": "2023-12-12", "36": "2023-12-13", "37": "2023-12-14",
                            "38": "2023-12-15", "39": "2023-12-16", "40": "2023-12-17", "41": "2023-12-18",
                            "42": "2023-12-19", "43": "2023-12-20"},
            "Bestellingen per dag": {"0": 1, "1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "6": 1, "7": 4, "8": 4, "9": 1,
                                     "10": 1, "11": 4, "12": 6, "13": 1, "14": 2, "15": 2, "16": 3, "17": 17, "18": 2,
                                     "19": 5, "20": 2, "21": 5, "22": 7, "23": 1, "24": 1, "25": 4, "26": 4, "27": 5,
                                     "28": 4, "29": 14, "30": 15, "31": 8, "32": 18, "33": 27, "34": 20, "35": 28,
                                     "36": 24, "37": 23, "38": 45, "39": 58, "40": 37, "41": 38, "42": 52, "43": 29},
            "Totaal aantal bestellingen": {"0": 1, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 11, "8": 15,
                                           "9": 16, "10": 17, "11": 21, "12": 27, "13": 28, "14": 30, "15": 32,
                                           "16": 35,
                                           "17": 52, "18": 54, "19": 59, "20": 61, "21": 66, "22": 73, "23": 74,
                                           "24": 75,
                                           "25": 79, "26": 83, "27": 88, "28": 92, "29": 106, "30": 121, "31": 129,
                                           "32": 147, "33": 174, "34": 194, "35": 222, "36": 246, "37": 269, "38": 314,
                                           "39": 372, "40": 409, "41": 447, "42": 499, "43": 528},
            "Jaar": {"0": "2020", "1": "2020", "2": "2020", "3": "2020", "4": "2020", "5": "2020", "6": "2020",
                     "7": "2020", "8": "2020", "9": "2020", "10": "2020", "11": "2020", "12": "2020", "13": "2020",
                     "14": "2020", "15": "2020", "16": "2020", "17": "2020", "18": "2020", "19": "2020", "20": "2020",
                     "21": "2020", "22": "2020", "23": "2020", "24": "2020", "25": "2020", "26": "2020", "27": "2020",
                     "28": "2020", "29": "2020", "30": "2020", "31": "2020", "32": "2020", "33": "2020", "34": "2020",
                     "35": "2020", "36": "2020", "37": "2020", "38": "2020", "39": "2020", "40": "2020", "41": "2020",
                     "42": "2020", "43": "2020"},
            "Totaal aantal personen": {"0": 5.6, "1": 11.2, "2": 16.8, "3": 22.4, "4": 28.0, "5": 33.6, "6": 39.2,
                                       "7": 61.6, "8": 84.0, "9": 89.6, "10": 95.2, "11": 117.6, "12": 151.2,
                                       "13": 156.8,
                                       "14": 168.0, "15": 179.2, "16": 196.0, "17": 291.2, "18": 302.4, "19": 330.4,
                                       "20": 341.6, "21": 369.6, "22": 408.8, "23": 414.4, "24": 420.0, "25": 442.4,
                                       "26": 464.8, "27": 492.8, "28": 515.2, "29": 593.6, "30": 677.6, "31": 722.4,
                                       "32": 823.2, "33": 974.4, "34": 1086.4, "35": 1243.2, "36": 1377.6, "37": 1506.4,
                                       "38": 1758.4, "39": 2083.2, "40": 2290.4, "41": 2503.2, "42": 2794.4,
                                       "43": 2956.8}}
        data_2021 = {
            "Besteldatum": {"0": "2023-09-28", "1": "2023-10-10", "2": "2023-10-12", "3": "2023-10-13",
                            "4": "2023-10-16",
                            "5": "2023-10-21", "6": "2023-10-22", "7": "2023-10-25", "8": "2023-10-26",
                            "9": "2023-10-29",
                            "10": "2023-10-31", "11": "2023-11-01", "12": "2023-11-02", "13": "2023-11-04",
                            "14": "2023-11-05", "15": "2023-11-06", "16": "2023-11-07", "17": "2023-11-08",
                            "18": "2023-11-09", "19": "2023-11-10", "20": "2023-11-11", "21": "2023-11-12",
                            "22": "2023-11-13", "23": "2023-11-14", "24": "2023-11-15", "25": "2023-11-16",
                            "26": "2023-11-17", "27": "2023-11-18", "28": "2023-11-19", "29": "2023-11-20",
                            "30": "2023-11-21", "31": "2023-11-22", "32": "2023-11-23", "33": "2023-11-24",
                            "34": "2023-11-25", "35": "2023-11-26", "36": "2023-11-27", "37": "2023-11-28",
                            "38": "2023-11-29", "39": "2023-11-30", "40": "2023-12-01", "41": "2023-12-02",
                            "42": "2023-12-03", "43": "2023-12-04", "44": "2023-12-05", "45": "2023-12-06",
                            "46": "2023-12-07", "47": "2023-12-08", "48": "2023-12-09", "49": "2023-12-10",
                            "50": "2023-12-11", "51": "2023-12-12", "52": "2023-12-13", "53": "2023-12-14",
                            "54": "2023-12-15", "55": "2023-12-16", "56": "2023-12-17", "57": "2023-12-18",
                            "58": "2023-12-19"},
            "Bestellingen per dag": {"0": 1, "1": 2, "2": 2, "3": 1, "4": 1, "5": 1, "6": 1, "7": 1, "8": 2, "9": 2,
                                     "10": 4, "11": 1, "12": 1, "13": 2, "14": 2, "15": 3, "16": 1, "17": 1, "18": 2,
                                     "19": 3, "20": 5, "21": 2, "22": 4, "23": 2, "24": 4, "25": 3, "26": 3, "27": 2,
                                     "28": 2, "29": 2, "30": 8, "31": 5, "32": 3, "33": 11, "34": 6, "35": 7, "36": 8,
                                     "37": 26, "38": 9, "39": 10, "40": 13, "41": 4, "42": 9, "43": 17, "44": 21,
                                     "45": 35,
                                     "46": 33, "47": 37, "48": 33, "49": 50, "50": 45, "51": 52, "52": 42, "53": 53,
                                     "54": 78, "55": 66, "56": 60, "57": 57, "58": 59},
            "Totaal aantal bestellingen": {"0": 1, "1": 3, "2": 5, "3": 6, "4": 7, "5": 8, "6": 9, "7": 10, "8": 12,
                                           "9": 14, "10": 18, "11": 19, "12": 20, "13": 22, "14": 24, "15": 27,
                                           "16": 28,
                                           "17": 29, "18": 31, "19": 34, "20": 39, "21": 41, "22": 45, "23": 47,
                                           "24": 51,
                                           "25": 54, "26": 57, "27": 59, "28": 61, "29": 63, "30": 71, "31": 76,
                                           "32": 79,
                                           "33": 90, "34": 96, "35": 103, "36": 111, "37": 137, "38": 146, "39": 156,
                                           "40": 169, "41": 173, "42": 182, "43": 199, "44": 220, "45": 255, "46": 288,
                                           "47": 325, "48": 358, "49": 408, "50": 453, "51": 505, "52": 547, "53": 600,
                                           "54": 678, "55": 744, "56": 804, "57": 861, "58": 920},
            "Jaar": {"0": "2021", "1": "2021", "2": "2021", "3": "2021", "4": "2021", "5": "2021", "6": "2021",
                     "7": "2021", "8": "2021", "9": "2021", "10": "2021", "11": "2021", "12": "2021", "13": "2021",
                     "14": "2021", "15": "2021", "16": "2021", "17": "2021", "18": "2021", "19": "2021", "20": "2021",
                     "21": "2021", "22": "2021", "23": "2021", "24": "2021", "25": "2021", "26": "2021", "27": "2021",
                     "28": "2021", "29": "2021", "30": "2021", "31": "2021", "32": "2021", "33": "2021", "34": "2021",
                     "35": "2021", "36": "2021", "37": "2021", "38": "2021", "39": "2021", "40": "2021", "41": "2021",
                     "42": "2021", "43": "2021", "44": "2021", "45": "2021", "46": "2021", "47": "2021", "48": "2021",
                     "49": "2021", "50": "2021", "51": "2021", "52": "2021", "53": "2021", "54": "2021", "55": "2021",
                     "56": "2021", "57": "2021", "58": "2021"},
            "Totaal aantal personen": {"0": 5.6, "1": 16.8, "2": 28.0, "3": 33.6, "4": 39.2, "5": 44.8, "6": 50.4,
                                       "7": 56.0, "8": 67.2, "9": 78.4, "10": 100.8, "11": 106.4, "12": 112.0,
                                       "13": 123.2,
                                       "14": 134.4, "15": 151.2, "16": 156.8, "17": 162.4, "18": 173.6, "19": 190.4,
                                       "20": 218.4, "21": 229.6, "22": 252.0, "23": 263.2, "24": 285.6, "25": 302.4,
                                       "26": 319.2, "27": 330.4, "28": 341.6, "29": 352.8, "30": 397.6, "31": 425.6,
                                       "32": 442.4, "33": 504.0, "34": 537.6, "35": 576.8, "36": 621.6, "37": 767.2,
                                       "38": 817.6, "39": 873.6, "40": 946.4, "41": 968.8, "42": 1019.2, "43": 1114.4,
                                       "44": 1232.0, "45": 1428.0, "46": 1612.8, "47": 1820.0, "48": 2004.8,
                                       "49": 2284.8,
                                       "50": 2536.8, "51": 2828.0, "52": 3063.2, "53": 3360.0, "54": 3796.8,
                                       "55": 4166.4,
                                       "56": 4502.4, "57": 4821.6, "58": 5152.0}}
        data_2022 = {
            "Besteldatum": {"0": "2023-09-09", "1": "2023-09-16", "2": "2023-09-17", "3": "2023-09-21",
                            "4": "2023-09-29",
                            "5": "2023-09-30", "6": "2023-10-04", "7": "2023-10-08", "8": "2023-10-10",
                            "9": "2023-10-11",
                            "10": "2023-10-12", "11": "2023-10-13", "12": "2023-10-15", "13": "2023-10-17",
                            "14": "2023-10-18", "15": "2023-10-21", "16": "2023-10-22", "17": "2023-10-23",
                            "18": "2023-10-24", "19": "2023-10-25", "20": "2023-10-26", "21": "2023-10-28",
                            "22": "2023-10-30", "23": "2023-10-31", "24": "2023-11-01", "25": "2023-11-02",
                            "26": "2023-11-04", "27": "2023-11-05", "28": "2023-11-06", "29": "2023-11-07",
                            "30": "2023-11-08", "31": "2023-11-09", "32": "2023-11-10", "33": "2023-11-11",
                            "34": "2023-11-12", "35": "2023-11-13", "36": "2023-11-14", "37": "2023-11-15",
                            "38": "2023-11-16", "39": "2023-11-17", "40": "2023-11-18", "41": "2023-11-19",
                            "42": "2023-11-20", "43": "2023-11-21", "44": "2023-11-22", "45": "2023-11-23",
                            "46": "2023-11-24", "47": "2023-11-25", "48": "2023-11-26", "49": "2023-11-27",
                            "50": "2023-11-28", "51": "2023-11-29", "52": "2023-11-30", "53": "2023-12-01",
                            "54": "2023-12-02", "55": "2023-12-03", "56": "2023-12-04", "57": "2023-12-05",
                            "58": "2023-12-06", "59": "2023-12-07", "60": "2023-12-08", "61": "2023-12-09",
                            "62": "2023-12-10", "63": "2023-12-11", "64": "2023-12-12", "65": "2023-12-13",
                            "66": "2023-12-14", "67": "2023-12-15", "68": "2023-12-16", "69": "2023-12-17",
                            "70": "2023-12-18", "71": "2023-12-19", "72": "2023-12-20"},
            "Bestellingen per dag": {"0": 1, "1": 1, "2": 1, "3": 1, "4": 1, "5": 1, "6": 1, "7": 2, "8": 1, "9": 2,
                                     "10": 2, "11": 1, "12": 1, "13": 2, "14": 1, "15": 2, "16": 2, "17": 3, "18": 1,
                                     "19": 1, "20": 1, "21": 2, "22": 4, "23": 5, "24": 3, "25": 5, "26": 4, "27": 1,
                                     "28": 3, "29": 5, "30": 4, "31": 2, "32": 5, "33": 2, "34": 3, "35": 2, "36": 3,
                                     "37": 5, "38": 7, "39": 4, "40": 3, "41": 6, "42": 7, "43": 11, "44": 7, "45": 7,
                                     "46": 14, "47": 13, "48": 15, "49": 22, "50": 14, "51": 17, "52": 15, "53": 14,
                                     "54": 11, "55": 17, "56": 34, "57": 17, "58": 22, "59": 29, "60": 37, "61": 26,
                                     "62": 35, "63": 43, "64": 44, "65": 57, "66": 51, "67": 47, "68": 42, "69": 67,
                                     "70": 62, "71": 40, "72": 2},
            "Totaal aantal bestellingen": {"0": 1, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 9, "8": 10,
                                           "9": 12, "10": 14, "11": 15, "12": 16, "13": 18, "14": 19, "15": 21,
                                           "16": 23,
                                           "17": 26, "18": 27, "19": 28, "20": 29, "21": 31, "22": 35, "23": 40,
                                           "24": 43,
                                           "25": 48, "26": 52, "27": 53, "28": 56, "29": 61, "30": 65, "31": 67,
                                           "32": 72,
                                           "33": 74, "34": 77, "35": 79, "36": 82, "37": 87, "38": 94, "39": 98,
                                           "40": 101,
                                           "41": 107, "42": 114, "43": 125, "44": 132, "45": 139, "46": 153, "47": 166,
                                           "48": 181, "49": 203, "50": 217, "51": 234, "52": 249, "53": 263, "54": 274,
                                           "55": 291, "56": 325, "57": 342, "58": 364, "59": 393, "60": 430, "61": 456,
                                           "62": 491, "63": 534, "64": 578, "65": 635, "66": 686, "67": 733, "68": 775,
                                           "69": 842, "70": 904, "71": 944, "72": 946},
            "Jaar": {"0": "2022", "1": "2022", "2": "2022", "3": "2022", "4": "2022", "5": "2022", "6": "2022",
                     "7": "2022", "8": "2022", "9": "2022", "10": "2022", "11": "2022", "12": "2022", "13": "2022",
                     "14": "2022", "15": "2022", "16": "2022", "17": "2022", "18": "2022", "19": "2022", "20": "2022",
                     "21": "2022", "22": "2022", "23": "2022", "24": "2022", "25": "2022", "26": "2022", "27": "2022",
                     "28": "2022", "29": "2022", "30": "2022", "31": "2022", "32": "2022", "33": "2022", "34": "2022",
                     "35": "2022", "36": "2022", "37": "2022", "38": "2022", "39": "2022", "40": "2022", "41": "2022",
                     "42": "2022", "43": "2022", "44": "2022", "45": "2022", "46": "2022", "47": "2022", "48": "2022",
                     "49": "2022", "50": "2022", "51": "2022", "52": "2022", "53": "2022", "54": "2022", "55": "2022",
                     "56": "2022", "57": "2022", "58": "2022", "59": "2022", "60": "2022", "61": "2022", "62": "2022",
                     "63": "2022", "64": "2022", "65": "2022", "66": "2022", "67": "2022", "68": "2022", "69": "2022",
                     "70": "2022", "71": "2022", "72": "2022"},
            "Totaal aantal personen": {"0": 5.6, "1": 11.2, "2": 16.8, "3": 22.4, "4": 28.0, "5": 33.6, "6": 39.2,
                                       "7": 50.4, "8": 56.0, "9": 67.2, "10": 78.4, "11": 84.0, "12": 89.6, "13": 100.8,
                                       "14": 106.4, "15": 117.6, "16": 128.8, "17": 145.6, "18": 151.2, "19": 156.8,
                                       "20": 162.4, "21": 173.6, "22": 196.0, "23": 224.0, "24": 240.8, "25": 268.8,
                                       "26": 291.2, "27": 296.8, "28": 313.6, "29": 341.6, "30": 364.0, "31": 375.2,
                                       "32": 403.2, "33": 414.4, "34": 431.2, "35": 442.4, "36": 459.2, "37": 487.2,
                                       "38": 526.4, "39": 548.8, "40": 565.6, "41": 599.2, "42": 638.4, "43": 700.0,
                                       "44": 739.2, "45": 778.4, "46": 856.8, "47": 929.6, "48": 1013.6, "49": 1136.8,
                                       "50": 1215.2, "51": 1310.4, "52": 1394.4, "53": 1472.8, "54": 1534.4,
                                       "55": 1629.6,
                                       "56": 1820.0, "57": 1915.2, "58": 2038.4, "59": 2200.8, "60": 2408.0,
                                       "61": 2553.6,
                                       "62": 2749.6, "63": 2990.4, "64": 3236.8, "65": 3556.0, "66": 3841.6,
                                       "67": 4104.8,
                                       "68": 4340.0, "69": 4715.2, "70": 5062.4, "71": 5286.4, "72": 5297.6}}

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
        # fig.update_yaxes(range = ["28-8","18-12"])
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