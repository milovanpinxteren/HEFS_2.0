
from hefs.apis import kerstdiner2022api

from .models import ApiUrls


class GetOrders:
    def __init__(self, user_id):
        print('GET ORDERS')
        api = ApiUrls.objects.get(user_id=user_id).api
        # exec(api)   #uncomment this after developing


