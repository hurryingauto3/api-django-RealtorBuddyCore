from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from . import views  # Make sure to import your DRF viewsets here if they are defined in views.py

# DRF router for API endpoints
router = DefaultRouter()
router.register(r'api', views.BuildingViewSet)  # Update with the correct viewset if necessary

urlpatterns = [
    path('updateAddressAbr/', views.updateAddressAbbreviations, name='updateAddressAbr`'),
    # Traditional Django views for web interface
    # path('', views.index, name=   'building-index'),
    # path('list/', BuildingListView.as_view(), name='building-list'),
    # path('detail/<int:pk>/', BuildingDetailView.as_view(), name='building-detail'),
    # path('create/', BuildingCreateView.as_view(), name='building-new'),
    # path('edit/<int:pk>/', BuildingUpdateView.as_view(), name='building-edit'),
    # path('delete/<int:pk>/', BuildingDeleteView.as_view(), name='building-delete'),
    
    # DRF API URLs
    path('', include(router.urls)),  # This includes router generated URL patterns for the API
]
