from django.urls import path, include
from .views import *
from . import (
    views,
)  # Make sure to import your DRF viewsets here if they are defined in views.py


from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ClientEmailDefinitionViewSet, ClientEmailOutReachRulesetViewSet, ClientViewSet

router = DefaultRouter()
router.register(r"emails", ClientEmailDefinitionViewSet)
router.register(r"rulesets", ClientEmailOutReachRulesetViewSet)
router.register(r"clients", ClientViewSet)

urlpatterns = [
    path("list_email", views.list_email, name="list_email"),
    path("read_email", views.read_email, name="read_email"),
    path("send_email", views.send_email, name="send_email"),
    path("send_email_to_client", views.sendEmailsToClients, name="send_email_to_client"),
    path("", include(router.urls)),
    
]