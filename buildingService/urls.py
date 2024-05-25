from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import (
    views,
)  # Make sure to import your DRF viewsets here if they are defined in views.py

# DRF router for API endpoints
router = DefaultRouter()
router.register(
    r"building", views.BuildingViewSet
)  # This registers the BuildingViewSet under the 'buildings' endpoint

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
    path("", include(router.urls)),  # Includes the router's URLs into the project
    path(
        "cooperation/<int:cooperation_id>/",
        views.CooperationHistoryViewSet.as_view({"get": "list"}),
        name="cooperation",
    ),
]
