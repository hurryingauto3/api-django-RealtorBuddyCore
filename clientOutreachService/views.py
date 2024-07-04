import logging
from .utils import GmailServiceAccountAPI, construct_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets
from .models import clientEmailDefinition, clientEmailOutReachRuleset
from .serializers import (
    ClientEmailDefinitionSerializer,
    ClientEmailOutReachRulesetSerializer,
)

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def list_email(request):
    # Get the message ID from the request
    # msg_id = request.GET.get("msg_id")
    user = request.GET.get("user")
    query = request.GET.get("query")

    if not user:
        return JsonResponse({"error": "Missing user parameter"}, status=400)

    # Get the GmailServiceAccountAPI instance
    gmail_service = GmailServiceAccountAPI(delegated_user=f"{user}@realtor-buddy.com")

    try:
        # Read the email
        message = gmail_service.list_email(query=query)
        return JsonResponse({"message": message})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def read_email(request):
    # Get the message ID from the request
    msg_id = request.GET.get("id")
    user = request.GET.get("user")

    if not msg_id:
        return JsonResponse({"error": "Missing msg_id parameter"}, status=400)

    if not user:
        return JsonResponse({"error": "Missing user parameter"}, status=400)

    # Get the GmailServiceAccountAPI instance
    gmail_service = GmailServiceAccountAPI(delegated_user=f"{user}@realtor-buddy.com")

    try:
        # Read the email
        message = gmail_service.read_email(msg_id)
        return JsonResponse({"message": message})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def send_email(request):
    # Get the message ID from the request
    to = request.GET.get("to")
    name = request.GET.get("name")
    message_id = request.GET.get("message_id")
    user = request.GET.get("user")

    if not to:
        return JsonResponse({"error": "Missing to parameter"}, status=400)

    if not message_id:
        return JsonResponse({"error": "Missing message_id parameter"}, status=400)

    if not user:
        return JsonResponse({"error": "Missing user parameter"}, status=400)

    # Get the GmailServiceAccountAPI instance
    user = f"{user}@realtor-buddy.com"
    gmail_service = GmailServiceAccountAPI(delegated_user=user)

    try:
        # Send the email
        to = f"{name} <{to}>"
        context = {"name": name.split(" ")[0]}
        message = construct_email(to, message_id, context)
        sent = gmail_service.send_email(message)
        return JsonResponse({"message": sent})
    except Exception as e:
        return JsonResponse(
            {"error": str(e), "traceback": str(e.with_traceback())}, status=500
        )


class ClientEmailDefinitionViewSet(viewsets.ModelViewSet):
    queryset = clientEmailDefinition.objects.all()
    serializer_class = ClientEmailDefinitionSerializer


class ClientEmailOutReachRulesetViewSet(viewsets.ModelViewSet):
    queryset = clientEmailOutReachRuleset.objects.all()
    serializer_class = ClientEmailOutReachRulesetSerializer
