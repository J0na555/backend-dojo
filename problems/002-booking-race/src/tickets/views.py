from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Event


@csrf_exempt
def book_ticket(request, event_id):
    """Book one ticket for an event.

    BUG: The available-tickets check and the increment are not atomic.
    Under concurrent requests both can pass the check, causing oversell.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({"error": "Event not found"}, status=404)

    if event.available_tickets <= 0:
        return JsonResponse({"error": "Sold out"}, status=400)

    # Non-atomic read-modify-write — race window here.
    event.tickets_sold += 1
    event.save(update_fields=["tickets_sold"])

    return JsonResponse({
        "tickets_sold": event.tickets_sold,
        "remaining": event.available_tickets,
    })


def event_detail(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)
    return JsonResponse({
        "name": event.name,
        "total_tickets": event.total_tickets,
        "tickets_sold": event.tickets_sold,
        "available": event.available_tickets,
    })
