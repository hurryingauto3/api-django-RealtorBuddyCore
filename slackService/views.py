import json
import logging
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from urllib.parse import parse_qs
import requests  # Make sure to import requests for HTTP operations

from twilioService.utils import sendTextMessage
from twilioService.llm_utils import getUpdatedBuildingInformation

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def handleActionBuildingAssistant(request):
    # Read the raw data
    raw_data = request.body.decode("utf-8")

    try:
        # Parse URL-encoded data
        parsed_data = parse_qs(raw_data)

        # Extract payload from parsed data and decode JSON
        payload_json = parsed_data.get("payload", [])[0]
        payload = json.loads(payload_json)
        user_id = payload.get("user", {}).get("id")
        response_url = payload.get("response_url")
        building_id, from_number = (
            payload.get("actions", [{}])[0].get("value", "").split("_")
        )
        building_url = (
            f"https://api.realtor-buddy.com/buildings/building/{building_id}"
        )
        # # Get updated building information
        # body = getUpdatedBuildingInformation(building_id)
        # # Send a text message with the building information updated
        # sendTextMessage(from_number, body)

        # Send the updated information back to Slack using the response_url
        slack_response = {
            "text": f"Updated information for <{building_url}|building> sent to {from_number} by <@{user_id}>",
            "replace_original": "true",
        }
        response = requests.post(response_url, json=slack_response, timeout=3)
        if response.status_code != 200:
            logger.error("Failed to post response back to Slack: %s", response.text)

        return HttpResponse(content="Update sent successfully", status=200)

    except (json.JSONDecodeError, IndexError) as e:
        logger.error("Error processing the data: %s", e)
        return JsonResponse({"error": "Bad request"}, status=400)
