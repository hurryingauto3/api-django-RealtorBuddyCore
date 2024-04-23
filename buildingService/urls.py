from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from . import (
    views,
)  # Make sure to import your DRF viewsets here if they are defined in views.py

# DRF router for API endpoints
router = DefaultRouter()
router.register(
    r"api", views.BuildingViewSet
)  # Update with the correct viewset if necessary

urlpatterns = [
    path(
        "updateAddressAbr/", views.updateAddressAbbreviations, name="updateAddressAbr`"
    ),
    path(
        "convertAndInsertBuildingData/",
        views.convertAndInsertBuildingData,
        name="convertAndInsertBuildingData",
    ),
    path("normalizeAddress/", views.getNormalizedAddress, name="normalizeAddress"),
    # DRF API URLs
    path(
        "", include(router.urls)
    ),  # This includes router generated URL patterns for the API
]
