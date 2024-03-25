
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import TextMessage, WhatsAppMessage
from .utils import getTextMessageBuildingSearchResponse, sendTextMessage

from twilio.twiml.messaging_response import MessagingResponse, Message

import logging

logger = logging.getLogger(__name__)

def sendTextMessageEP(request):
    try:
        message = sendTextMessage(
            to_number='+18722450045',
            body='test'
        )
        return HttpResponse(str(message), content_type="application/xml")
    
    except Exception as e:
        return HttpResponse(str(e), status=500)

@require_POST
@csrf_exempt  # Twilio requests will not have a CSRF token
def textMessageReceived(request):
    
    data = request.POST
    text_message = TextMessage(
        sid=data.get('MessageSid', ''),  # Note: 'sid' is based on your response structure
        body=data.get('Body', ''),
        num_segments=data.get('NumSegments', ''),
        direction=data.get('Direction', ''),
        from_number=data.get('From', ''),
        to_number=data.get('To', ''),
        date_updated=data.get('DateUpdated', None),
        price=data.get('Price', None),
        error_message=data.get('ErrorMessage', ''),
        uri=data.get('Uri', ''),
        account_sid=data.get('AccountSid', ''),
        num_media=data.get('NumMedia', ''),
        date_created=data.get('DateCreated', None),
        status=data.get('MessageStatus', ''),  # Note: 'status' is based on your response structure
        date_sent=data.get('DateSent', None),
        messaging_service_sid=data.get('MessagingServiceSid', ''),
        error_code=data.get('ErrorCode', None),
        price_unit=data.get('PriceUnit', ''),
        api_version=data.get('ApiVersion', ''),
        # Add subresource_uris if you have a JSON field
    )
    text_message.save()
    
    if data.get('MessageStatus') == 'received':
        
        response = MessagingResponse()
        search_result = getTextMessageBuildingSearchResponse(data.get('Body'))

        if search_result:
            response.append(Message(body="Hello! Thanks for your message. Here are the search results:"))
            for building in search_result:
                response.append(Message(body=building))
            response.append(Message(body="We hope you found what you were looking for - RealtorBuddy"))
        
        else:
            response.append(Message(body="Hello! Thanks for your message."))
            response.append(Message(body="We will get back to you soon."))

        return HttpResponse(str(response), content_type="application/xml")
    
    else:
        return HttpResponse(status=200)
        


@require_POST
@csrf_exempt
def whatsappMessageReceived(request):
    data = request.POST
    # Create and save a new WhatsAppMessage instance
    whatsapp_message = WhatsAppMessage(
        sms_message_sid=data.get('SmsMessageSid'),
        num_media=data.get('NumMedia'),
        profile_name=data.get('ProfileName', ''),  # Optional field
        message_type=data.get('MessageType'),
        sms_sid=data.get('SmsSid'),
        wa_id=data.get('WaId'),
        sms_status=data.get('SmsStatus'),
        body=data.get('Body'),
        to_number=data.get('To'),
        num_segments=data.get('NumSegments'),
        referral_num_media=data.get('ReferralNumMedia', ''),  # Optional field
        message_sid=data.get('MessageSid'),
        account_sid=data.get('AccountSid'),
        from_number=data.get('From'),
        api_version=data.get('ApiVersion'),
    )
    whatsapp_message.save()
    
    if data.get('SmsStatus') == 'received':
        
        response = MessagingResponse()
        search_result = getTextMessageBuildingSearchResponse(data.get('Body'))

        if search_result:
            response.append(Message(body="Hello! Thanks for your message. Here are the search results:"))
            for building in search_result:
                response.append(Message(body=building))
            response.append(Message(body="We hope you found what you were looking for - RealtorBuddy"))
        
        else:
            response.append(Message(body="Hello! Thanks for your message."))
            response.append(Message(body="We will get back to you soon."))

        return HttpResponse(str(response), content_type="application/xml")
    
    else:
        return HttpResponse(status=200)

@csrf_exempt
@require_POST
def textMessageBuildingSearch(request):
    data = request.POST
    message_body = data.get('Body', '').strip()
    response = getTextMessageBuildingSearchResponse(message_body)
    return HttpResponse(str(response), content_type="application/xml")
