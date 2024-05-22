from django.urls import path, include
from .views import *
from . import views  # Make sure to import your DRF viewsets here if they are defined in views.py


urlpatterns = [
    path('handleActionBuildingAssistant/', views.handleActionBuildingAssistant, name='handleActionBuildingAssistant'),
]
