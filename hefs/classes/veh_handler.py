from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from hefs.models import AlgemeneInformatie, Orderline, Orders, ApiUrls, LeverancierUserLink
from hefs.sql_commands import SqlCommands
from django.db import connection


class VehHandler():
    def handle_veh(self, organisations_to_show, user):
        try:
            prognosegetal_diner = AlgemeneInformatie.objects.get(naam='prognosegetal_diner').waarde
            prognosegetal_brunch = AlgemeneInformatie.objects.get(naam='prognosegetal_brunch').waarde
            prognosegetal_gourmet = AlgemeneInformatie.objects.get(naam='prognosegetal_gourmet').waarde
            aantal_hoofdgerechten = AlgemeneInformatie.objects.get(naam='aantalHoofdgerechten').waarde
            aantal_brunch = Orderline.objects.filter(productSKU__in=[700, 701]).aggregate(Sum('aantal'))['aantal__sum']
            aantal_gourmet = Orderline.objects.filter(productSKU__in=[750, 751, 752, 753]).aggregate(Sum('aantal'))['aantal__sum']
            # aantal_gourmet = 0
            try:
                prognosefractie_diner = prognosegetal_diner / aantal_hoofdgerechten
            except Exception as e:
                prognosefractie_diner = 0
            try:
                prognosefractie_brunch = prognosegetal_brunch / aantal_brunch
            except Exception as e:
                prognosefractie_brunch = 0
            try:
                prognosefractie_gourmet = prognosegetal_gourmet / aantal_gourmet
            except Exception as e:
                prognosefractie_gourmet = 0
            aantal_orders = AlgemeneInformatie.objects.get(naam='aantalOrders').waarde
        except Exception as e:
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
            sql_commands = SqlCommands()
            if user.groups.filter(name='leverancier').exists():
                try:
                    leverancier_link = LeverancierUserLink.objects.get(user_id=user.id)
                    leverancier_id = leverancier_link.leverancier.id
                    sql_veh = sql_commands.get_veh_command_for_leverancier(dates, leverancier_id)
                except LeverancierUserLink.DoesNotExist:
                    return {
                        'table': '', 'column_headers': '',
                        'veh_is_empty': 'Geen leverancier gelinkt aan dit account.'
                    }
            else:
                sql_veh = sql_commands.get_veh_command(dates)

        cursor.execute(sql_veh)
        veh = cursor.fetchall()
        veh = sorted(veh, key=lambda tup: tup[1])
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
            productcode = row[2]
            if productcode in ['750', '751', '752', '753']:
                prognose = row_total * prognosefractie_gourmet
                total_prognose = total_of_product * prognosefractie_gourmet
                updated_row = (*updated_row, prognose, total_prognose)
            if gang == "7" and productcode not in ['750', '751', '752', '753']:
                prognose = row_total * prognosefractie_brunch
                total_prognose = total_of_product * prognosefractie_brunch
                updated_row = (*updated_row, prognose, total_prognose)
            elif gang != "7":
                prognose = row_total * prognosefractie_diner
                total_prognose = total_of_product * prognosefractie_diner
                updated_row = (*updated_row, prognose, total_prognose)
            veh[i] = updated_row

        orders_per_date_dict = {}
        for date in dates:
            print(date)
            no_orders = Orders.objects.filter(afleverdatum=date[0]).count()
            orders_per_date_dict[str(date[0])] = no_orders

        context = {'table': veh, 'column_headers': date_array, 'prognosegetal_diner': prognosegetal_diner,
                   'prognosegetal_brunch': prognosegetal_brunch, 'prognosegetal_gourmet': prognosegetal_gourmet,
                   'aantal_hoofdgerechten': aantal_hoofdgerechten, 'aantal_orders': aantal_orders,
                   'aantal_brunch': aantal_brunch, 'aantal_gourmet': aantal_gourmet, 'orders_per_date_dict': orders_per_date_dict}

        return context
