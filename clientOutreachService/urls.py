from django.urls import path, include
from .views import *
from . import (
    views,
)  # Make sure to import your DRF viewsets here if they are defined in views.py


from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    ClientEmailDefinitionViewSet,
    ClientEmailOutReachRulesetViewSet,
    ClientViewSet,
)

router = DefaultRouter()
router.register(r"emails", ClientEmailDefinitionViewSet)
router.register(r"rulesets", ClientEmailOutReachRulesetViewSet)
router.register(r"clients", ClientViewSet)

urlpatterns = [
    path("send_email", views.send_email, name="send_email"),
    path("send_emails_bulk", views.sendEmailsToClients, name="sendEmailsToClients"),
    path("", include(router.urls)),
]
