from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from hefs.models import AlgemeneInformatie, Orderline, Orders, ApiUrls
from hefs.sql_commands import SqlCommands
from django.db import connection


class VehHandler():
    def handle_veh(self, organisations_to_show):
        try:
            prognosegetal_diner = AlgemeneInformatie.objects.get(naam='prognosegetal_diner').waarde
            prognosegetal_brunch = AlgemeneInformatie.objects.get(naam='prognosegetal_brunch').waarde
            prognosegetal_gourmet = AlgemeneInformatie.objects.get(naam='prognosegetal_gourmet').waarde
            aantal_hoofdgerechten = AlgemeneInformatie.objects.get(naam='aantalHoofdgerechten').waarde
            aantal_brunch = Orderline.objects.filter(productSKU__in=[110, 111]).aggregate(Sum('aantal'))['aantal__sum']  # TODO: change to brunch
            aantal_gourmet = Orderline.objects.filter(productSKU__in=[110, 111]).aggregate(Sum('aantal'))['aantal__sum']  # TODO: change to gourmet
            prognosefractie_diner = prognosegetal_diner / aantal_hoofdgerechten
            prognosefractie_brunch = prognosegetal_brunch / aantal_brunch
            prognosefractie_gourmet = prognosegetal_gourmet / aantal_gourmet
            aantal_orders = AlgemeneInformatie.objects.get(naam='aantalOrders').waarde
        except (ObjectDoesNotExist, ZeroDivisionError):
            prognosegetal_diner = 0
            prognosegetal_brunch = 0
            prognosegetal_gourmet = 0
            aantal_hoofdgerechten = 0
            aantal_brunch = 0
            aantal_gourmet = 0
            prognosefractie_diner = 0
            prognosefractie_brunch = 0
            prognosefractie_gourmet = 0
            aantal_orders = 0

        dates = Orders.objects.filter(organisatieID__in=organisations_to_show).order_by('afleverdatum').values_list(
            'afleverdatum').distinct()
        date_array = []
        if not dates:
            return {'table': '', 'column_headers': '',
                       'veh_is_empty': 'Geen producten gevonden, weet u zeker dat u met de juiste account bent ingelogd?'}
        else:
            for date in dates:
                date_array.append(date)
            cursor = connection.cursor()
            sql_veh = SqlCommands().get_veh_command(date_array)
            cursor.execute(sql_veh)
            veh = cursor.fetchall()

        for i, row in enumerate(veh):
            productcode = row[2]
            products = [tup for tup in veh if productcode in tup]
            total_of_product = 0
            for product in products:
                verpakkingseenheid = int(product[1][4])
                aantal = int(product[3 + len(date_array)])
                total_of_product += verpakkingseenheid * aantal
                updated_row = (*row, total_of_product)
            row_total = row[3 + len(date_array)]
            gang = row[1][0]
            if gang == "3":  # TODO: change to "7"
                prognose = row_total * prognosefractie_brunch
                total_prognose = total_of_product * prognosefractie_brunch
                updated_row = (*updated_row, prognose, total_prognose)
            elif gang == "9":  # Gourmet
                prognose = row_total * prognosefractie_gourmet
                total_prognose = total_of_product * prognosefractie_gourmet
                updated_row = (*updated_row, prognose, total_prognose)
            elif gang != "7" and gang != "9":
                prognose = row_total * prognosefractie_diner
                total_prognose = total_of_product * prognosefractie_diner
                updated_row = (*updated_row, prognose, total_prognose)
            veh[i] = updated_row

        context = {'table': veh, 'column_headers': date_array, 'prognosegetal_diner': prognosegetal_diner,
                   'prognosegetal_brunch': prognosegetal_brunch, 'prognosegetal_gourmet': prognosegetal_gourmet,
                   'aantal_hoofdgerechten': aantal_hoofdgerechten, 'aantal_orders': aantal_orders,
                   'aantal_brunch': aantal_brunch, 'aantal_gourmet': aantal_gourmet}

        return context