from django.urls import path
from . import views

urlpatterns = [
    path("events/", views.stripeEventHandler, name="stripeEventHandler")
]
