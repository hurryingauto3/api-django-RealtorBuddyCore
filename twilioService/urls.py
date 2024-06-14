from django.urls import path, include
from .views import *
from . import views  # Make sure to import your DRF viewsets here if they are defined in views.py


urlpatterns = [
    # path('sendTextMessage/', views.sendTextMessageEP, name='sendTextMessage'),
    path('textMessageReceived/', views.textMessageReceived, name='textMessageRecieved'),
    # path('internalTextMessageReceived/', views.internalTextMessageReceived, name='internalTextMessageReceived'),
    # path('whatsappMessageReceived/', views.whatsappMessageReceived, name='whatsappMessageRecieved'),
    # path('textMessageBuildingSearch/', views.textMessageBuildingSearch, name='textMessageBuildingSearch'),
]
