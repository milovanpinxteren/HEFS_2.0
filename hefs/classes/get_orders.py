
from hefs.apis import kerstdiner2022api
from hefs.apis import kerstdiner2023api
from hefs.apis import paasdiner2023api
from hefs.apis.paasdiner2023api import Paasdiner2023API
from hefs.apis.kerstdiner2023api import Kerstdiner2023API
from hefs.apis.paasontbijt2024api import Paasontbijt2024API
from hefs.apis.kerstdiner2024api import Kerstdiner2024API

from hefs.models import ApiUrls


class GetOrders:
    def __init__(self, user_id):
        print('GET ORDERS')
        api = ApiUrls.objects.get(user_id=user_id).api
        # Paasdiner2023API()
        exec(api)   #uncomment this after developing


