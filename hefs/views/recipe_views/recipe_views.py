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

        HalfproductenIngredienten.objects.create(
            halfproduct=halfproduct,
            ingredient=ingredient,
            quantity=quantity
        )
        if form.is_valid():
            form.save()
            return redirect('show_halfproducten')  # Redirect to the same page after submission
    else:
        form = HalfproductenIngredientenForm()

    return render(request, 'recipes/halfproducten.html', {'form': form})


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
    halfproduct_name = request.GET.get('halfproduct_name')
    try:
        halfproduct = Halfproducten.objects.get(naam=halfproduct_name)
        ingredients = HalfproductenIngredienten.objects.filter(halfproduct=halfproduct)
        ingredients_list = [
            {'name': hi.ingredient.naam, 'quantity': hi.quantity, 'meeteenheid': hi.ingredient.meeteenheid} for hi in
            ingredients]
        return JsonResponse(ingredients_list, safe=False)
    except Halfproducten.DoesNotExist:
        return JsonResponse([], safe=False)


def show_productinfo(request):
    return render(request, 'recipes/productinfo.html')


def show_ingredienten(request):
    return render(request, 'recipes/ingredienten.html')
