from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
import json
from .models import Event


@csrf_exempt
def book_ticket(request, event_id):
    """Book one ticket for an event using atomic F() update."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    # Atomically increment tickets_sold only if tickets remain
    updated = Event.objects.filter(
        id=event_id,
        tickets_sold__lt=F("total_tickets"),
    ).update(tickets_sold=F("tickets_sold") + 1)

    if updated == 0:
        # Either the event doesn't exist or it's sold out
        if not Event.objects.filter(id=event_id).exists():
            return JsonResponse({"error": "Event not found"}, status=404)
        return JsonResponse({"error": "Sold out"}, status=400)

    event = Event.objects.get(id=event_id)
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
