from hefs.models import Productinfo, Ingredienten, Halfproducten


class HalfProductShower:
    def show_half_products(self, veh):
        stored_products = []
        table_data = {}
        for product in veh:
            productID = product[1]
            productcode = product[2]
            total_product_quantity = product[-3]
            total_predicted_quantity = product[-1]
            if productcode not in stored_products:
                product_info = Productinfo.objects.get(productID=productID)
                table_data[productcode] = {'product': product_info.productnaam}
                halfproducts = Halfproducten.objects.filter(product=product_info)
                table_data[productcode]['halfproducts'] = {}
                for halfproduct in halfproducts:
                    table_data[productcode]['halfproducts'][halfproduct.naam] = {
                        'data': [halfproduct.bereidingskosten_per_eenheid,
                                 halfproduct.meeteenheid,
                                 halfproduct.nodig_per_portie,
                                 halfproduct.bereidingswijze,
                                 halfproduct.nodig_per_portie * total_product_quantity,
                                 halfproduct.nodig_per_portie * total_predicted_quantity,
                                 halfproduct.bereidingskosten_per_eenheid * total_product_quantity,
                                 halfproduct.bereidingskosten_per_eenheid * total_predicted_quantity,
                                 ]}
                    ingredients = Ingredienten.objects.filter(halfproduct=halfproduct)
                    table_data[productcode]['halfproducts'][halfproduct.naam]['ingredients'] = {}
                    for ingredient in ingredients:
                        table_data[productcode]['halfproducts'][halfproduct.naam]['ingredients'][
                            ingredient.naam] = [ingredient.meeteenheid, ingredient.nodig_per_portie,
                                                ingredient.kosten_per_eenheid,
                                                ingredient.nodig_per_portie * total_product_quantity,
                                                ingredient.nodig_per_portie * total_predicted_quantity,
                                                ingredient.kosten_per_eenheid * total_product_quantity,
                                                ingredient.kosten_per_eenheid * total_predicted_quantity,
                                                ]

                stored_products.append(productcode)
        return table_data
