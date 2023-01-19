from hefs.models import NewOrders, Orders, Orderline


class AddOrders():
    def __init__(self):
        self.validate_orders()
        self.add_to_orderfile()


    def validate_orders(self):
        print('VALIDEER ORDERS')


    def add_to_orderfile(self):
        print('ADD TO ORDERFILE')
        self.all_new_orders = NewOrders.objects.all()
        #split new orders into Orders and Orderline

        #get all unique conversieIDS
        # for loop over uniques:
        #     filter over neworders
        #     voeg toe aan Orders
        #     order = order.objects.create
        #
        #     for loop over filter:
        #         voeg toe aan Orderline (order=order)