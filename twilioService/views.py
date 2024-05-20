import time
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import TextMessage, WhatsAppMessage
from .utils import getTextMessageBuildingSearchResponse, sendTextMessage
from .llm_utils import distillSearchItemFromQuery, displaySearchResultsToCustomer

from twilio.twiml.messaging_response import MessagingResponse, Message

import logging

logger = logging.getLogger(__name__)


def sendTextMessageEP(request):
    try:
        message = sendTextMessage(to_number="+18722450045", body="test")
        return HttpResponse(str(message), content_type="application/xml")

    except Exception as e:
        return HttpResponse(str(e), status=500)


@require_POST
@csrf_exempt  # Twilio requests will not have a CSRF token
def textMessageReceived(request):
    
    data = request.POST  # Parse the POST data from the request body

    textmessage = TextMessage(
        to_country=data.get("ToCountry", ""),
        to_state=data.get("ToState", ""),
        sms_message_sid=data.get("SmsMessageSid", ""),
        num_media=data.get("NumMedia", ""),
        to_city=data.get("ToCity", ""),
        from_zip=data.get("FromZip", ""),
        sms_sid=data.get("SmsSid", ""),
        from_state=data.get("FromState", ""),
        sms_status=data.get("SmsStatus", ""),
        from_city=data.get("FromCity", ""),
        body=data.get("Body", ""),
        from_country=data.get("FromCountry", ""),
        to_number=data.get("To", ""),
        to_zip=data.get("ToZip", ""),
        num_segments=data.get("NumSegments", ""),
        message_sid=data.get("MessageSid", ""),
        account_sid=data.get("AccountSid", ""),
        from_number=data.get("From", ""),
        api_version=data.get("ApiVersion", ""),
    )
    
    textmessage.save()
    
    if textmessage.sms_status == "received":
        
        # Stripe check workflow
        # Manual building information audit workflow

        response = MessagingResponse()
        message_raw = textmessage.body
        search_result = getTextMessageBuildingSearchResponse(message_raw)

        if search_result:
            response_text = displaySearchResultsToCustomer(message_raw, search_result)
            response.append(Message(body=response_text))

        else:
            response.append(
                Message(
                    body="Hello! Thanks for your message. We will get back to you soon."
                )
            )

        return HttpResponse(str(response), content_type="application/xml")

    else:
        return HttpResponse(status=200)
    
    
# Slack hook for greenlighting building information output
# Accepts slack hook
# Checks if building was updated
# If building was updated, sends message to customer
# If building was not updated, sends message to slack reporting channel

# Not for production use
@require_POST
@csrf_exempt
def whatsappMessageReceived(request):
    
    data = request.POST  # Parse the POST data from the request body
    # Create and save a new WhatsAppMessage instance
    whatsapp_message = WhatsAppMessage(
        sms_message_sid=data.get("SmsMessageSid"),
        num_media=data.get("NumMedia"),
        profile_name=data.get("ProfileName", ""),  # Optional field
        message_type=data.get("MessageType"),
        sms_sid=data.get("SmsSid"),
        wa_id=data.get("WaId"),
        sms_status=data.get("SmsStatus"),
        body=data.get("Body"),
        to_number=data.get("To"),
        num_segments=data.get("NumSegments"),
        referral_num_media=data.get("ReferralNumMedia", ""),  # Optional field
        message_sid=data.get("MessageSid"),
        account_sid=data.get("AccountSid"),
        from_number=data.get("From"),
        api_version=data.get("ApiVersion"),
    )
    whatsapp_message.save()

    if data.get("MessageStatus") == "received":

        response = MessagingResponse()
        message_raw = data.get("Body", "")
        search_result = getTextMessageBuildingSearchResponse(message_raw)

        if search_result:
            response_text = displaySearchResultsToCustomer(message_raw, search_result)
            response.append(Message(body=response_text))

        else:
            response.append(
                Message(
                    body="Hello! Thanks for your message. We will get back to you soon."
                )
            )

        return HttpResponse(str(response), content_type="application/xml")

    else:
        return HttpResponse(status=200)

@csrf_exempt
@require_POST
def internalTextMessageReceived(request):
    
    try:
        data = json.loads(request.body)  # Parse the JSON data from the request body
    except json.JSONDecodeError:
        logger.error("Error decoding JSON")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    message_raw = data.get("Body", None)
    # message_distilled = distillSearchItemFromQuery(message_raw)
    message_distilled = None
    start_time = time.time()
    search_result = getTextMessageBuildingSearchResponse(message_distilled if message_distilled else message_raw)
    search_time = round(time.time() - start_time, 2)
    
    start_time = time.time()
    output = displaySearchResultsToCustomer(message_raw, search_result)
    ai_present_time = round(time.time() - start_time, 2)
    
    return JsonResponse(
        {
            "message_raw": message_raw,
            "message_distilled": message_distilled,
            "search_result": search_result,
            "output": output,
            "search_time": search_time,
            "ai_present_time": ai_present_time,
        }
    )
