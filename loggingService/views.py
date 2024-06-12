import logging
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.dateparse import parse_datetime
from .models import CloudFlareLog
from .utils import sendHTTPLogToSlackChannel

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def receiveCloudFlareLogs(request):
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)

        # Extract necessary fields
        timestamp = parse_datetime(data.get("timestamp"))
        url = data.get("url")
        method = data.get("method")
        headers = data.get("headers")
        cf = data.get("cf")

        # Save the log to the database
        log_entry = CloudFlareLog(
            timestamp=timestamp, url=url, method=method, headers=headers, cf=cf
        )
        log_entry.save()

        # Extract location info
        city = cf.get("city", "Unknown city")
        region = cf.get("region", "Unknown region")
        country = cf.get("country", "Unknown country")
        # Format the Slack message
        slack_message = f"{method}; {url}; {city}, {region}, {country}"
        # Send the log to the Slack channel
        sendHTTPLogToSlackChannel(slack_message)

        return JsonResponse({"status": "Update sent successfully"}, status=200)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
