import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .utils import getTextMessageBuildingSearchResponse

@csrf_exempt
@require_POST
def textMessageBuildingSearch(request):
    message_body = request.POST.get('Body', '').strip()
    response = getTextMessageBuildingSearchResponse(message_body)
    return HttpResponse(str(response), content_type="application/xml")
