import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from django.db.models import F
from django.test import TransactionTestCase, Client
from tickets.models import Event

class TestBookingRace(TransactionTestCase):
    def test_sequential_bookings_respect_capacity(self):
        event = Event.objects.create(name="Concert", total_tickets=5)
        c = Client()
        for i in range(5):
            resp = c.post(f"/events/{event.id}/book")
            self.assertEqual(resp.status_code, 200, f"Request {i+1}")
        resp = c.post(f"/events/{event.id}/book")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["error"], "Sold out")

    def test_concurrent_readers_dont_oversell(self):
        event = Event.objects.create(name="Concert", total_tickets=10)
        updated1 = Event.objects.filter(
            id=event.id, tickets_sold__lt=F("total_tickets")
        ).update(tickets_sold=F("tickets_sold") + 1)
        updated2 = Event.objects.filter(
            id=event.id, tickets_sold__lt=F("total_tickets")
        ).update(tickets_sold=F("tickets_sold") + 1)
        self.assertEqual(updated1, 1)
        self.assertEqual(updated2, 1)
        event.refresh_from_db()
        self.assertEqual(event.tickets_sold, 2)
