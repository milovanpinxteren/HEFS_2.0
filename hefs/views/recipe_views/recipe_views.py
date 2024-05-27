from django.shortcuts import render

from hefs.models import ApiUrls, Halfproducten


def show_halfproducten(request):
    organisations_to_show = ApiUrls.objects.get(user_id=request.user.id).organisatieIDs
    half_products = Halfproducten.objects.all().prefetch_related('ingredienten')
    context = {'half_products' : half_products}
    return render(request, 'recipes/halfproducten.html', context)


def show_productinfo(request):
    return render(request, 'recipes/productinfo.html')

def show_ingredienten(request):
    return render(request, 'recipes/ingredienten.html')