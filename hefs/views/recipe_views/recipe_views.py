from collections import defaultdict

from django.db import IntegrityError
from django.db.models import Sum, F
from django.http import JsonResponse
from django.shortcuts import render

from hefs.forms import HalfproductenIngredientenForm, ProductenHalfproductenForm
from hefs.models import Halfproducten, Ingredienten, HalfproductenIngredienten, Productinfo, \
    ProductenHalfproducts, PickItems, ProductenIngredienten


def show_halfproducten(request):
    if request.method == 'POST':
        form = HalfproductenIngredientenForm(request.POST)
        halfproduct_name = form['halfproduct'].value()
        ingredient_name = form['ingredient'].value()
        quantity = form['quantity'].value()
        halfproduct = Halfproducten.objects.get(naam=halfproduct_name)
        ingredient = Ingredienten.objects.get(naam=ingredient_name)
        try:
            halfproducten_ingredienten, created = HalfproductenIngredienten.objects.get_or_create(
                halfproduct=halfproduct, ingredient=ingredient, defaults={'quantity': quantity}
            )
            if not created:  # object was not created, so it was retrieved
                if float(quantity) > 0:
                    halfproducten_ingredienten.quantity = quantity  # update the quantity
                    halfproducten_ingredienten.save()
                elif float(quantity) <= 0:
                    halfproducten_ingredienten.delete()
        except IntegrityError:
            print('A Constraint Error Occured.')
            context = {'form': form, 'msg': 'A Constraint Error Occured.'}
            return render(request, 'recipes/halfproducten.html', context)
        form = HalfproductenIngredientenForm(initial={'halfproduct': halfproduct_name})
        context = {'form': form, 'default_halfproduct': halfproduct_name}
        return render(request, 'recipes/halfproducten.html', context)
    else:
        form = HalfproductenIngredientenForm()
        context = {'form': form}

    return render(request, 'recipes/halfproducten.html', context)


# def show_productinfo(request):
#     if request.method == 'POST':
#         form = ProductenHalfproductenForm(request.POST)
#         halfproduct_name = form['halfproduct'].value()
#         product_name = form['product'].value()
#         quantity = form['quantity'].value()
#         halfproduct = Halfproducten.objects.get(naam=halfproduct_name)
#         product = Productinfo.objects.filter(productnaam=product_name)[0]
#         product_code = product.productcode
#         try:
#             halfproducten_ingredienten, created = ProductenHalfproducts.objects.get_or_create(
#                 product=product, productcode=product_code, halfproduct=halfproduct, defaults={'quantity': quantity}
#             )
#             if not created:  # object was not created, so it was retrieved
#                 if float(quantity) > 0:
#                     halfproducten_ingredienten.quantity = quantity  # update the quantity
#                     halfproducten_ingredienten.save()
#                 elif float(quantity) <= 0:
#                     halfproducten_ingredienten.delete()
#             form = ProductenHalfproductenForm(initial={'product': product_name})
#             context = {'form': form, 'default_product': product_name}
#         except IntegrityError:
#             print('A Constraint Error Occured.')
#             context = {'form': form, 'msg': 'A Constraint Error Occured.'}
#     else:
#         form = ProductenHalfproductenForm()
#         context = {'form': form}
#     return render(request, 'recipes/productinfo.html', context)
#

def show_productinfo(request):
    if request.method == 'POST':
        form = ProductenHalfproductenForm(request.POST)
        halfproduct_name = form['halfproduct'].value()
        product_name = form['product'].value()
        quantity = form['quantity'].value()
        halfproduct = None
        ingredient = None
        try:
            halfproduct = Halfproducten.objects.get(naam=halfproduct_name)
        except Halfproducten.DoesNotExist:
            pass
        if not halfproduct:
            try:
                ingredient = Ingredienten.objects.get(naam=halfproduct_name)
            except Ingredienten.DoesNotExist:
                pass

        product = Productinfo.objects.filter(productnaam=product_name)[0]
        product_code = product.productcode

        try:
            if halfproduct:
                # If a halfproduct exists, proceed like before
                product_halfproduct, created = ProductenHalfproducts.objects.get_or_create(
                    product=product, productcode=product_code, halfproduct=halfproduct, defaults={'quantity': quantity}
                )
                if not created:  # object was not created, so it was retrieved
                    if float(quantity) > 0:
                        product_halfproduct.quantity = quantity  # update the quantity
                        product_halfproduct.save()
                    elif float(quantity) <= 0:
                        product_halfproduct.delete()

            if ingredient:
                # If an ingredient exists, check or create in ProductenIngredienten
                product_ingredient, created = ProductenIngredienten.objects.get_or_create(
                    product=product, productcode=product_code, ingredient=ingredient, defaults={'quantity': quantity}
                )
                if not created:  # object was not created, so it was retrieved
                    if float(quantity) > 0:
                        product_ingredient.quantity = quantity  # update the quantity
                        product_ingredient.save()
                    elif float(quantity) <= 0:
                        product_ingredient.delete()

            form = ProductenHalfproductenForm(initial={'product': product_name})
            context = {'form': form, 'default_product': product_name}

        except IntegrityError:
            print('A Constraint Error Occured.')
            context = {'form': form, 'msg': 'A Constraint Error Occured.'}
    else:
        form = ProductenHalfproductenForm()
        context = {'form': form}

    return render(request, 'recipes/productinfo.html', context)


def show_ingredienten(request):
    return render(request, 'recipes/ingredienten.html')


def ingredient_autocomplete(request):
    if 'term' in request.GET:
        qs = Ingredienten.objects.filter(naam__icontains=request.GET.get('term'))
        names = list()
        for ingredient in qs:
            names.append(ingredient.naam)
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)


def halfproduct_autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        halfproduct_qs = Halfproducten.objects.filter(naam__icontains=term)
        ingredienten_qs = Ingredienten.objects.filter(naam__icontains=term)
        names = [obj.naam for obj in halfproduct_qs]
        names += [obj.naam for obj in ingredienten_qs]
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)


def product_autocomplete(request):
    if 'term' in request.GET:
        qs = Productinfo.objects.filter(productnaam__icontains=(request.GET.get('term')))
        names = list()
        for product in qs:
            if product.productnaam not in names:
                names.append(product.productnaam)
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)


def get_ingredients_for_halfproduct(request):
    if request.GET.get('halfproduct_name'):
        halfproduct_name = request.GET.get('halfproduct_name')
    elif request.POST['halfproduct']:
        halfproduct_name = request.POST['halfproduct']
    try:
        halfproduct = Halfproducten.objects.get(naam=halfproduct_name)
        ingredients = HalfproductenIngredienten.objects.filter(halfproduct=halfproduct)
        ingredients_list = [
            {'name': hi.ingredient.naam, 'quantity': hi.quantity, 'meeteenheid': hi.ingredient.meeteenheid} for hi in
            ingredients]
        ingredients_list.append({'bereidingswijze': halfproduct.bereidingswijze, 'meeteenheid': halfproduct.meeteenheid,
                                 'nodig_per_portie': str(halfproduct.nodig_per_portie),
                                 'bereidingskosten_per_eenheid': str(halfproduct.bereidingskosten_per_eenheid)})
        return JsonResponse(ingredients_list, safe=False)
    except Halfproducten.DoesNotExist:
        return JsonResponse([], safe=False)


def get_halfproducts_and_ingredients(request):
    ingredients_dict = {}
    if request.GET.get('product_name'):
        product_name = request.GET.get('product_name')
    elif request.POST['product']:
        product_name = request.POST['product']
    try:
        product = Productinfo.objects.filter(productnaam=product_name)[0]
        product_code = product.productcode
        halfproduct_objects = ProductenHalfproducts.objects.filter(productcode=product_code)
        ingredient_objects = ProductenIngredienten.objects.filter(productcode=product_code)
        for halfproduct in halfproduct_objects:
            ingredients_list = []
            ingredients = HalfproductenIngredienten.objects.filter(halfproduct=halfproduct.halfproduct)
            for hi in ingredients:
                ingredients_list.append({
                    'name': hi.ingredient.naam,
                    'quantity': hi.quantity * halfproduct.quantity,
                    'meeteenheid': hi.ingredient.meeteenheid,
                    'kosten_per_eenheid': (hi.quantity * halfproduct.quantity) * hi.ingredient.kosten_per_eenheid
                })
            ingredients_list.append({
                'name': 'Bereiding: ' + halfproduct.halfproduct.naam,
                'quantity': halfproduct.halfproduct.bruikbare_hoeveelheid,
                'meeteenheid': halfproduct.halfproduct.meeteenheid,
                'kosten_per_eenheid': halfproduct.quantity * halfproduct.halfproduct.bereidingskosten_per_eenheid
            })
            ingredients_dict[halfproduct.halfproduct.naam] = ingredients_list
        ingredients_list = []
        for ingredient in ingredient_objects:
            ingredients_list.append({
                'name': ingredient.ingredient.naam,
                'quantity': ingredient.quantity,
                'meeteenheid': ingredient.ingredient.meeteenheid,
                'kosten_per_eenheid': ingredient.quantity * ingredient.ingredient.kosten_per_eenheid
            })
        ingredients_dict["Ingredienten"] = ingredients_list
        return JsonResponse(ingredients_dict, safe=False)
    except Halfproducten.DoesNotExist:
        return JsonResponse([], safe=False)


def get_ingredients_list(request):
    # annotated_pickitems = (
    #     PickItems.objects.annotate(
    #         halfproduct_id=F('product__productenhalfproducts__halfproduct_id'),
    #         halfproduct_quantity=F('product__productenhalfproducts__quantity'),
    #         ingredient_id=F('product__productenhalfproducts__halfproduct__halfproducteningredienten__ingredient_id'),
    #         ingredient_quantity=F('product__productenhalfproducts__halfproduct__halfproducteningredienten__quantity'),
    #         ingredient_name=F('product__productenhalfproducts__halfproduct__halfproducteningredienten__ingredient__naam'),
    #         kosten_per_eenheid=F(
    #             'product__productenhalfproducts__halfproduct__halfproducteningredienten__ingredient__kosten_per_eenheid')
    #
    #     ).values(
    #         'ingredient_id', 'ingredient_name', 'product__productnaam', 'hoeveelheid', 'halfproduct_quantity',
    #         'ingredient_quantity', 'kosten_per_eenheid'
    #     ).annotate(
    #         total_quantity=Sum(F('hoeveelheid') * F('halfproduct_quantity') * F('ingredient_quantity'),
    #                            output_field=DecimalField())
    #     )
    # )

    # annotated_pickitems = (
    #     PickItems.objects.annotate(
    #         halfproduct_id=F('product__productenhalfproducts__halfproduct_id'),
    #         halfproduct_quantity=F('product__productenhalfproducts__quantity'),
    #         ingredient_id=F('product__productenhalfproducts__halfproduct__halfproducteningredienten__ingredient_id'),
    #         ingredient_quantity=F('product__productenhalfproducts__halfproduct__halfproducteningredienten__quantity'),
    #         ingredient_name=F(
    #             'product__productenhalfproducts__halfproduct__halfproducteningredienten__ingredient__naam'),
    #         kosten_per_eenheid=F(
    #             'product__productenhalfproducts__halfproduct__halfproducteningredienten__ingredient__kosten_per_eenheid'),
    #
    #         direct_ingredient_id=F('product__producteningredienten__ingredient_id'),
    #         direct_ingredient_quantity=F('product__producteningredienten__quantity'),
    #         direct_ingredient_name=F('product__producteningredienten__ingredient__naam'),
    #         direct_kosten_per_eenheid=F('product__producteningredienten__ingredient__kosten_per_eenheid')
    #
    #     ).values(
    #         'ingredient_id', 'ingredient_name', 'product__productnaam', 'hoeveelheid', 'halfproduct_quantity',
    #         'ingredient_quantity',
    #         'kosten_per_eenheid', 'direct_ingredient_id', 'direct_ingredient_quantity', 'direct_ingredient_name',
    #         'direct_kosten_per_eenheid'
    #
    #     ).annotate(
    #         total_quantity=Sum(F('hoeveelheid') * F('halfproduct_quantity') * F('ingredient_quantity'),
    #                            output_field=DecimalField()),
    #         direct_total_quantity=Sum(F('hoeveelheid') * F('direct_ingredient_quantity'),
    #                                   output_field=DecimalField())
    #     )
    # )

    annotated_pickitems = PickItems.objects.values('product__productcode').annotate(
        total_hoeveelheid=Sum(F('hoeveelheid') * F('product__verpakkingseenheid'))
    ).values()

    def get_safe_value(value):
        return value if value is not None else 0

    # Aggregate the total quantities of each ingredient
    total_ingredients = defaultdict(lambda: {'quantity': 0, 'cost': 0})
    for item in annotated_pickitems:
        total_quantity = get_safe_value(item['total_hoeveelheid'])
        product_code = item['product_id'][1:4]
        halfproducts = ProductenHalfproducts.objects.filter(productcode=product_code)
        for halfproduct_instance in halfproducts:
            ingredients = HalfproductenIngredienten.objects.filter(halfproduct=halfproduct_instance.id)
            for ingredient_instance in ingredients:
                ingredient_name = ingredient_instance.ingredient.naam
                quantity = float(ingredient_instance.quantity) * float(halfproduct_instance.quantity) * float(
                    total_quantity)
                costs = float(ingredient_instance.ingredient.kosten_per_eenheid) * float(
                    ingredient_instance.quantity) * float(halfproduct_instance.quantity) * float(total_quantity)
                total_ingredients[ingredient_name]['quantity'] += quantity
                total_ingredients[ingredient_name]['cost'] += costs

        direct_ingredients = ProductenIngredienten.objects.filter(productcode=product_code)
        for direct_ingredient_instance in direct_ingredients:
            ingredient_name = direct_ingredient_instance.ingredient.naam
            quantity = float(direct_ingredient_instance.quantity) * float(total_quantity)
            costs = float(direct_ingredient_instance.ingredient.kosten_per_eenheid) * float(
                direct_ingredient_instance.quantity) * float(total_quantity)
            total_ingredients[ingredient_name]['quantity'] += quantity
            total_ingredients[ingredient_name]['cost'] += costs

    context = {'total_ingredients': total_ingredients.items()}

    return render(request, 'recipes/ingredients_list_page.html', context)
