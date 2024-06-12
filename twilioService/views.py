import time
import json
import logging
import datetime

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from twilio.twiml.messaging_response import MessagingResponse
from APIRealtorBuddyCore.config import STRIPE_PAYMENT_LINK
from stripeService.models import Customer, Subscription

from .models import TextMessage
from .utils import getTextMessageBuildingSearchResponse, sendTextMessage
from .llm_utils import displaySearchResultsToCustomer

logger = logging.getLogger(__name__)


def sendTextMessageEP(request):
    try:
        message = sendTextMessage(to_number="+18722450045", body="test")
        return HttpResponse(str(message), content_type="application/xml")

    except Exception as e:
        return HttpResponse(str(e), status=500)


@require_POST
@csrf_exempt
def textMessageReceived(request):
    data = request.POST
    textmessage, created = TextMessage.objects.update_or_create(
        sms_message_sid=data.get("SmsMessageSid", ""),
        defaults={
            "to_country": data.get("ToCountry", ""),
            "to_state": data.get("ToState", ""),
            "sms_message_sid": data.get("SmsMessageSid", ""),
            "num_media": data.get("NumMedia", ""),
            "to_city": data.get("ToCity", ""),
            "from_zip": data.get("FromZip", ""),
            "sms_sid": data.get("SmsSid", ""),
            "from_state": data.get("FromState", ""),
            "sms_status": data.get("SmsStatus", ""),
            "from_city": data.get("FromCity", ""),
            "body": data.get("Body", ""),
            "from_country": data.get("FromCountry", ""),
            "to_number": data.get("To", ""),
            "to_zip": data.get("ToZip", ""),
            "num_segments": data.get("NumSegments", ""),
            "message_sid": data.get("MessageSid", ""),
            "account_sid": data.get("AccountSid", ""),
            "from_number": data.get("From", ""),
            "api_version": data.get("ApiVersion", ""),
        },
    )
    if textmessage.sms_status != "received":
        return HttpResponse(status=200)
    
    if not created:
        return HttpResponse(status=200)

    try:
        response = MessagingResponse()
        stripe_customer = Customer.objects.get(phone=textmessage.from_number)
        stripe_subscription = (
            Subscription.objects.get(customer=stripe_customer)
            if stripe_customer
            else None
        )

        # Check if the subscription is active or has been canceled but the period has not ended yet
        if (
            stripe_subscription
            and stripe_subscription.status == "active"
            or (
                stripe_subscription
                and stripe_subscription.cancel_at_period_end
                and datetime.datetime.now() <= stripe_subscription.current_period_end
            )
        ):
            message_raw = textmessage.body
            search_result = getTextMessageBuildingSearchResponse(message_raw)
            response_text = (
                displaySearchResultsToCustomer(
                    message_raw, search_result, textmessage.from_number
                )
                if search_result
                else "Thank you for your message. We will get back to you soon."
            )
            response.message(response_text)

            # Inform the user if the subscription is ending soon
            if (
                stripe_subscription.cancel_at_period_end
                and datetime.datetime.now() <= stripe_subscription.current_period_end
            ):
                date = stripe_subscription.canceled_at.strftime("%Y-%m-%d")
                response.message(
                    f"Your subscription will end on {date}. To avoid interruption, please renew at: {STRIPE_PAYMENT_LINK}."
                )

        # Handle expired subscriptions
        elif datetime.datetime.now() > stripe_subscription.current_period_end:
            response.message(
                f"Your subscription has expired. To continue using our services, please renew at: {STRIPE_PAYMENT_LINK}."
            )

        return HttpResponse(str(response), content_type="application/xml")

    except (Customer.DoesNotExist, Subscription.DoesNotExist):
        previous_texts = TextMessage.objects.filter(
            from_number=textmessage.from_number
        ).count()

        if previous_texts <= 4:
            message_raw = textmessage.body
            search_result = getTextMessageBuildingSearchResponse(message_raw)
            response_text = (
                displaySearchResultsToCustomer(
                    message_raw, search_result, textmessage.from_number
                )
                if search_result
                else "Thank you for your message. We will get back to you soon."
            )
            response.message(response_text)
            if previous_texts > 2:
                response.message(
                    f"Hello! To continue enjoying our services uninterrupted, please subscribe at: {STRIPE_PAYMENT_LINK}."
                )
        else:
            response.message(
                f"Please subscribe to continue receiving our services at: {STRIPE_PAYMENT_LINK}."
            )

    return HttpResponse(str(response), content_type="application/xml")


# # Not for production use
# @require_POST
# @csrf_exempt
# def whatsappMessageReceived(request):
#     data = request.POST  # Parse the POST data from the request body
#     # Create and save a new WhatsAppMessage instance
#     whatsapp_message = WhatsAppMessage(
#         sms_message_sid=data.get("SmsMessageSid"),
#         num_media=data.get("NumMedia"),
#         profile_name=data.get("ProfileName", ""),  # Optional field
#         message_type=data.get("MessageType"),
#         sms_sid=data.get("SmsSid"),
#         wa_id=data.get("WaId"),
#         sms_status=data.get("SmsStatus"),
#         body=data.get("Body"),
#         to_number=data.get("To"),
#         num_segments=data.get("NumSegments"),
#         referral_num_media=data.get("ReferralNumMedia", ""),  # Optional field
#         message_sid=data.get("MessageSid"),
#         account_sid=data.get("AccountSid"),
#         from_number=data.get("From"),
#         api_version=data.get("ApiVersion"),
#     )
#     whatsapp_message.save()

#     if data.get("MessageStatus") == "received":

#         response = MessagingResponse()
#         message_raw = data.get("Body", "")
#         search_result = getTextMessageBuildingSearchResponse(message_raw)

#         if search_result:
#             response_text = displaySearchResultsToCustomer(message_raw, search_result)
#             response.append(Message(body=response_text))

#         else:
#             response.append(
#                 Message(
#                     body="Hello! Thanks for your message. We will get back to you soon."
#                 )
#             )

#         return HttpResponse(str(response), content_type="application/xml")

#     else:
#         return HttpResponse(status=200)


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
    search_result = getTextMessageBuildingSearchResponse(
        message_distilled if message_distilled else message_raw
    )
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
