
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect

from hefs.forms import HalfproductenIngredientenForm
from hefs.models import ApiUrls, Halfproducten, Ingredienten, HalfproductenIngredienten


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


def show_productinfo(request):
    return render(request, 'recipes/productinfo.html')


def show_ingredienten(request):
    return render(request, 'recipes/ingredienten.html')
