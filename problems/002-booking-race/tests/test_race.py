import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import threading
import pytest
from django.test import TransactionTestCase, Client

from tickets.models import Event


pytestmark = pytest.mark.django_db


class TestBookingRace(TransactionTestCase):
    def setUp(self):
        self.event = Event.objects.create(name="Concert", total_tickets=5)
        self.event_id = self.event.id

    def tearDown(self):
        from django.conf import settings
        db_path = settings.DATABASES["default"]["NAME"]
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except OSError:
                pass

    def test_sequential_bookings_respect_capacity(self):
        """Single-threaded: exactly 5 succeed, 6th is rejected."""
        c = Client()
        for i in range(5):
            resp = c.post(f"/events/{self.event_id}/book")
            self.assertEqual(
                resp.status_code, 200,
                f"Request {i+1} should succeed, got {resp.status_code}",
            )

        resp = c.post(f"/events/{self.event_id}/book")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()["error"], "Sold out")

    def test_concurrent_booking_race_lost_updates(self):
        """10 concurrent requests for 5 tickets — race causes lost updates.

        All threads read the same initial state, all pass the check,
        all write back the same incremented value — so the final count
        is wrong (lost updates).
        """
        results = []
        errors = []

        def make_request():
            try:
                c = Client()
                resp = c.post(f"/events/{self.event_id}/book")
                results.append(resp.status_code)
            except Exception as e:
                errors.append(str(e))

        threads = [threading.Thread(target=make_request) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Refresh event state from db
        self.event.refresh_from_db()
        successes = sum(1 for r in results if r == 200)

        # Without a race, exactly 5 succeed and tickets_sold=5.
        # With the race (lost updates/torn reads), fewer than 5 tickets
        # end up sold OR more than 5 succeed.
        correct = (successes == 5 and self.event.tickets_sold == 5)
        self.assertTrue(
            correct,
            f"Race condition: {successes} succeeded, "
            f"tickets_sold={self.event.tickets_sold}, expected 5 each",
        )
