from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=200)
    total_tickets = models.PositiveIntegerField()
    tickets_sold = models.PositiveIntegerField(default=0)

    @property
    def available_tickets(self):
        return self.total_tickets - self.tickets_sold
