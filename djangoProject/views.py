import json
from datetime import datetime, timedelta

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from hefs.models import Orders, Stop, TerminalLinks, FeeProducts


def index(request):
    return redirect('login')

@csrf_exempt
def get_terminal_for_user(request):
    if request.method == "GET":
        # Extract query parameters
        shop_id = request.GET.get("shopId")
        user_id = request.GET.get("userId")
        shop_domain = request.GET.get("shopDomain")
        location_id = request.GET.get("locationId")
        staff_member_id = request.GET.get("staffMemberId")
        # Validate mandatory fields
        if not shop_domain:
            return JsonResponse({"success": False, "error": "shopDomain is required"}, status=400)

        # Query the database for matching instances
        matching_shops = TerminalLinks.objects.filter(shop_domain=shop_domain)
        if user_id:
            matching_shops = matching_shops.filter(user_id=user_id)
        if matching_shops.count() > 1 and location_id:
            matching_shops = matching_shops.filter(location_id=location_id)
        if matching_shops.count() > 1 and staff_member_id:
            matching_shops = matching_shops.filter(staff_member_id=staff_member_id)
        if matching_shops.count() > 1 and shop_id:
            matching_shops = matching_shops.filter(shop_id=shop_id)

        # Get the first match or return an error if no match found
        shop = matching_shops.first()
        if not shop:
            return JsonResponse({"success": False, "error": "No matching terminal found"}, status=404)

        # Serialize the matching instances
        data = [
            {
                "shop_id": shop.shop_id,
                "user_id": shop.user_id,
                "shop_domain": shop.shop_domain,
                "location_id": shop.location_id,
                "staff_member_id": shop.staff_member_id,
                "terminal_id": shop.terminal_id,
                "api_key": shop.api_key,
            }
            for shop in matching_shops
        ]
        print(data)
        return JsonResponse({"success": True, "data": data}, status=200)
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)


def get_product_fees(request):
    fees_to_add = []
    if request.method == "GET":
        product_id = request.GET.get("productId")
        full_product_id = f'gid://shopify/Product/{product_id}'  # Replace with your actual product ID
        # SHOPIFY_STORE = "7c70bf.myshopify.com" #HOUSE OF BEERS
        SHOPIFY_STORE = "quickstart-767e0b0d.myshopify.com" #FEEFLEX
        # ACCESS_TOKEN = settings.HOB_ACCESS_TOKEN
        ACCESS_TOKEN = settings.FEEFLEX_API_KEY
        query = """
        query GetProductTags($id: ID!) {
          product(id: $id) {
            id
            title
            tags
          }
        }
        """
        variables = {
            "id": full_product_id
        }
        url = f"https://{SHOPIFY_STORE}/admin/api/2023-10/graphql.json"
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": ACCESS_TOKEN,
        }
        # Make the request
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        print(response)
        if response.status_code == 200:
            data = response.json()
            product = data.get("data", {}).get("product", {})

            if product:
                tags = product["tags"]
                for tag in tags:
                    if 'atiegeld' in tag:
                        print('tag', tag)
                        try:
                            fee_product = FeeProducts.objects.get(tag_name=tag)
                            variant_id = fee_product.fee_variant_id
                            fees_to_add.append(variant_id)
                        except ObjectDoesNotExist:
                            return JsonResponse({'variantsToAdd': fees_to_add}, status=200)
    return JsonResponse({'variantsToAdd': fees_to_add}, status=200)



@csrf_exempt
def track_order(request):
    if request.method == "POST":
        try:
            # Parse the incoming request body
            data = json.loads(request.body)
            conversie_id = data.get('orderID')
            email = data.get('email')

            # Retrieve the order using either conversieID or email
            if conversie_id:
                order = Orders.objects.filter(conversieID=conversie_id).first()
            elif email:
                order = Orders.objects.filter(emailadres=email).first()
            else:
                return JsonResponse({"error": "Please provide either an orderID or email"}, status=400)

            if not order:
                return JsonResponse({"error": "Bestelling niet gevonden"}, status=404)

            # Retrieve the related stop for the order
            stop = Stop.objects.filter(order=order).first()
            if not stop:
                return JsonResponse({"error": "Bestelling niet gevonden"}, status=404)

            # Prepare the response data
            response_data = {
                "orderID": order.conversieID,
                "email": order.emailadres,
                "route_number": stop.route.id if stop.route else None,
                # "sequence_number": stop.sequence_number,
                "arrival_time": f"{(datetime.combine(datetime.today(), stop.arrival_time) - timedelta(minutes=15)).strftime('%H:%M')} - "
                                f"{(datetime.combine(datetime.today(), stop.arrival_time) + timedelta(minutes=105)).strftime('%H:%M')}"
                if stop.arrival_time else None,
            }

            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)
