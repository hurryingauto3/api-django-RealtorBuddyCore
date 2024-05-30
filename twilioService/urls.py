from django.urls import path, include
from .views import *
from . import views  # Make sure to import your DRF viewsets here if they are defined in views.py


urlpatterns = [
    path('', dialer_page, name='dialer_home'),  # Serve the Dialer UI
    path('sendTextMessage/', views.sendTextMessageEP, name='sendTextMessage'),
    path('textMessageReceived/', views.textMessageReceived, name='textMessageRecieved'),
    
    path('generateToken/', generate_token, name='generateToken'),  # API to get token
    path('makeCall/', make_call, name='makeCall'),  # API to make a call
    # path('internalTextMessageReceived/', views.internalTextMessageReceived, name='internalTextMessageReceived'),
    # path('whatsappMessageReceived/', views.whatsappMessageReceived, name='whatsappMessageRecieved'),
    # path('textMessageBuildingSearch/', views.textMessageBuildingSearch, name='textMessageBuildingSearch'),
]
