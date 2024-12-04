import json

from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from hefs.models import Orders, Stop


def index(request):
    return redirect('login')



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
                return JsonResponse({"error": "Order not found"}, status=404)

            # Retrieve the related stop for the order
            stop = Stop.objects.filter(order=order).first()
            if not stop:
                return JsonResponse({"error": "Stop not found for this order"}, status=404)

            # Prepare the response data
            response_data = {
                "orderID": order.conversieID,
                "email": order.emailadres,
                "route_number": stop.route.id if stop.route else None,
                # "sequence_number": stop.sequence_number,
                "arrival_time": stop.arrival_time.strftime("%H:%M:%S") if stop.arrival_time else None,
                # "departure_time": stop.departure_time.strftime("%H:%M:%S") if stop.departure_time else None,
                # "visited": stop.visited,
                # "notes": stop.notes,
            }

            return JsonResponse(response_data, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid HTTP method"}, status=405)