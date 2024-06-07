
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect

from hefs.forms import HalfproductenIngredientenForm, ProductenHalfproductenForm
from hefs.models import ApiUrls, Halfproducten, Ingredienten, HalfproductenIngredienten, Productinfo, \
    ProductenHalfproducts


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
                halfproducten_ingredienten.quantity = quantity  # update the quantity
                halfproducten_ingredienten.save()
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

def show_productinfo(request):
    if request.method == 'POST':
        form = ProductenHalfproductenForm(request.POST)
        halfproduct_name = form['halfproduct'].value()
        product_name = form['product'].value()
        quantity = form['quantity'].value()
        halfproduct = Halfproducten.objects.get(naam=halfproduct_name)
        product = Productinfo.objects.filter(productnaam=product_name)[0]
        product_code = product.productcode
        try:
            halfproducten_ingredienten, created = ProductenHalfproducts.objects.get_or_create(
                product=product, productcode=product_code, halfproduct=halfproduct, defaults={'quantity': quantity}
            )
            if not created:  # object was not created, so it was retrieved
                halfproducten_ingredienten.quantity = quantity  # update the quantity
                halfproducten_ingredienten.save()
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
        qs = Halfproducten.objects.filter(naam__icontains=(request.GET.get('term')))
        names = list()
        for halfproduct in qs:
            names.append(halfproduct.naam)
        return JsonResponse(names, safe=False)
    return JsonResponse([], safe=False)


def product_autocomplete(request):
    if 'term' in request.GET:
        qs = Productinfo.objects.filter(productnaam__icontains=(request.GET.get('term')))
        names = list()
        for product in qs:
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
        for halfproduct in halfproduct_objects:
            ingredients_list = []
            ingredients = HalfproductenIngredienten.objects.filter(halfproduct=halfproduct.halfproduct)
            for hi in ingredients:
                ingredients_list.append({
                    'name': hi.ingredient.naam,  # Assuming Ingredienten has a 'name' field
                    'quantity': hi.quantity,  # Assuming Ingredienten has a 'quantity' field
                    'meeteenheid': hi.ingredient.meeteenheid  # Assuming Ingredienten has a 'meeteenheid' field
                })
            ingredients_dict[halfproduct.halfproduct.naam] = ingredients_list
        return JsonResponse(ingredients_dict, safe=False)
    except Halfproducten.DoesNotExist:
        return JsonResponse([], safe=False)



