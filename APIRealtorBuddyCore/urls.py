"""
URL configuration for APIRealtorBuddyCore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("buildings/", include("buildingService.urls")),
    path("twilio/", include("twilioService.urls")),
    path("slack/", include("slackService.urls")),
    path("stripe/", include("stripeService.urls")),
    path("logging/", include("loggingService.urls")),
    path("outreach/", include("clientOutreachService.urls")),
    # path('accounts/', include('allauth.urls')),
]
