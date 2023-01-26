import django_tables2 as tables

from hefs.models import PickItems


class VehTable(tables.Table):
    columns = tables.Column()
    class Meta:
        model = PickItems