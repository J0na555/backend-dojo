from django.urls import path
from . import views

urlpatterns = [
    path("events/<int:event_id>/book", views.book_ticket, name="book_ticket"),
    path("events/<int:event_id>", views.event_detail, name="event_detail"),
]
