import requests
import pandas as pd
import bs4 as bs
from django.db.models import Max
from hefs.models import Orders, Orderline, NewOrders


class Kerstdiner2022API:
    def __init__(self):
        self.get_orders()
        self.clean_orders()

    def get_orders(self):
        login_url = 'https://admin-panel.hapjesaanhuis.nl/accessifynet/accessifynet/Account/Login'
        username = 'm.v.pinxteren@kerstdiner.nl'
        password = 'Milovankerstdiner123'

        export_url = "https://admin-panel.hapjesaanhuis.nl/accessifynet/accessifynet/OrderExport/exportOrdersToExcel"
        last_date_dict = Orders.objects.aggregate(Max('besteldatum'))
        if next(iter(last_date_dict.values())) != None:
            begindatum = next(iter(last_date_dict.values()))
        else:
            begindatum = '8/9/2022'
        # begindatum = Orders.objects.aggregate(Max('besteldatum')).values().strftime("%d/%m/%Y")
        # einddatum = datetime.now() + timedelta(1)
        einddatum = '10/9/2022'
        resp = requests.get(login_url)

        verif_cookies = resp.cookies.items()[0]
        verification_token_with_id_key = verif_cookies[0]
        verification_token_with_id_value = verif_cookies[1]

        auth_cookies = resp.cookies.items()[1]
        auth_key = auth_cookies[0]
        auth_value = auth_cookies[1]

        soup = bs.BeautifulSoup(resp.content, "html.parser")
        verification_token = soup.find('input').get('value')

        headers = {'User-Agent': 'Mozilla/5.0',
                   'Content-Disposition': 'form-data'}

        payload = {'Email': username,
                   'Password': password,
                   'RememberMe': 'true',
                   '__RequestVerificationToken': verification_token,
                   'orderExportDateFrom': begindatum, 'orderExportDateTo': einddatum}

        cookies = {auth_key: auth_value,
                   verification_token_with_id_key: verification_token_with_id_value}

        with requests.Session() as s:
            r = s.post(login_url, headers=headers, data=payload, cookies=cookies)
            r = s.post(export_url, data=payload)

        self.new_orders = pd.read_excel(r.content)

    def clean_orders(self):
        relevant_org_ids = [304]

        self.new_orders = self.new_orders[self.new_orders['OrganisatieId'].notna()]
        self.new_orders = self.new_orders[self.new_orders['Product'].notna()]
        self.new_orders['OrganisatieId'] = self.new_orders['OrganisatieId'].astype(int)
        self.new_orders = self.new_orders[self.new_orders['OrganisatieId'].isin(relevant_org_ids)]
        self.new_orders = self.new_orders[~self.new_orders['Bedrijfsnaam'].isin(['DUBBELE ORDER', 'Dubbele order',
                                                                                 'dubbele order', 'Dubbele Order'])]
        self.new_orders = self.new_orders.reset_index()

        self.new_orders['Besteldatum'] = pd.to_datetime(self.new_orders['Besteldatum'], format="%d/%m/%Y %H:%M:%S")
        self.new_orders['Afleverdatum'] = pd.to_datetime(self.new_orders['Afleverdatum'], format="%d/%m/%Y")
        # self.new_orders['Aflevertijd'] = pd.to_timedelta(self.new_orders['Aflevertijd'])
        self.new_orders['Verzendkosten'] = self.new_orders['Verzendkosten'].str.replace(',', '.')
        self.new_orders['Verzendkosten'] = self.new_orders['Verzendkosten'].astype(float)
        self.new_orders['Korting'] = self.new_orders['Korting'].str.replace(',', '.')
        self.new_orders['Korting'] = self.new_orders['Korting'].astype(float)
        self.new_orders['OrderPrijs'] = self.new_orders['OrderPrijs'].str.replace(',', '.')
        self.new_orders['OrderPrijs'] = self.new_orders['OrderPrijs'].astype(float)
        self.new_orders['Totaal'] = self.new_orders['Totaal'].str.replace(',', '.')
        self.new_orders['Totaal'] = self.new_orders['Totaal'].astype(float)
        self.new_orders['Aantal'] = self.new_orders['Aantal'].astype(int)
        for orderline in range(0, len(self.new_orders)):
            print('Controle op bestaan in clean_orders', self.new_orders['ConversieId'][orderline])
            existing_order = Orderline.objects.filter(conversieID=self.new_orders['ConversieId'][orderline],
                                                      aantal=self.new_orders['Aantal'][orderline],
                                                      productSKU=self.new_orders['ProductSKU'][orderline])
            existing_new_order = NewOrders.objects.filter(conversieID=self.new_orders['ConversieId'][orderline],
                                                          aantal=self.new_orders['Aantal'][orderline],
                                                          productSKU=self.new_orders['ProductSKU'][orderline])

            if existing_order or existing_new_order:
                print('Order al aanwezig in database in clean_orders')
            else:
                print('Toevoegen aan database in clean_orders')
                NewOrders.objects.create(conversieID=self.new_orders['ConversieId'][orderline],
                                         besteldatum=self.new_orders['Besteldatum'][orderline],
                                         afleverdatum=self.new_orders['Afleverdatum'][orderline],
                                         aflevertijd=self.new_orders['Aflevertijd'][orderline],
                                         verzendkosten=self.new_orders['Verzendkosten'][orderline],
                                         korting=self.new_orders['Korting'][orderline],
                                         orderprijs=self.new_orders['OrderPrijs'][orderline],
                                         totaal=self.new_orders['Totaal'][orderline],
                                         aantal=self.new_orders['Aantal'][orderline],
                                         product=self.new_orders['Product'][orderline],
                                         productSKU=self.new_orders['ProductSKU'][orderline],
                                         organisatieID=self.new_orders['OrganisatieId'][orderline],
                                         organisatienaam=self.new_orders['Organisatie'][orderline],
                                         voornaam=self.new_orders['Voornaam'][orderline],
                                         achternaam=self.new_orders['Achternaam'][orderline],
                                         tussenvoegsel=self.new_orders['Tussenvoegsel'][orderline],
                                         emailadres=self.new_orders['Emailadres'][orderline],
                                         telefoonnummer=self.new_orders['Telefoonnummer'][orderline],
                                         straatnaam=self.new_orders['Straatnaam'][orderline],
                                         huisnummer=self.new_orders['Huisnummer'][orderline],
                                         postcode=self.new_orders['Postcode'][orderline],
                                         plaats=self.new_orders['Plaats'][orderline],
                                         land=self.new_orders['Land'][orderline],
                                         postadres_straatnaam=self.new_orders['Postadres Straatnaam'][orderline],
                                         postadres_huisnummer=self.new_orders['Postadres Huisnummer'][orderline],
                                         postadres_postcode=self.new_orders['Postadres Postcode'][orderline],
                                         postadres_plaats=self.new_orders['Postadres Plaats'][orderline],
                                         postadres_land=self.new_orders['Postadres Land'][orderline],
                                         opmerkingen=self.new_orders['Opmerkingen Klant'][orderline]
                                         )
                print('Toegevoegd aan database NewOrders', self.new_orders['ConversieId'][orderline])
