import requests
from django.conf import settings

from hefs.classes.error_handler import ErrorHandler


class InvoiceSender:
    def __init__(self):
        self.error_handler = ErrorHandler()
    def send_invoice(self, xml_string):
        username = 'Webshop'
        password = settings.MICROCASH_FTP_PASSWORD
        url = f"http://86.88.43.117/invoice.php?xml={xml_string}"
        response = requests.post(url=url, auth=(username, password))
        print(response.content)
        self.error_handler.log_error(str(response.content[:250]))

