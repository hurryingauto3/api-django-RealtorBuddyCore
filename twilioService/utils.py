import json
import logging
import requests
from APIRealtorBuddyCore.config import (
    TWILIO_ACCOUNT_SID_,
    TWILIO_AUTH_TOKEN_,
    TWILIO_NUMBER_,
)
from twilio.rest import Client

logger = logging.getLogger(__name__)


def sendTextMessage(to_number, body):
    
    try:
        client = Client(TWILIO_ACCOUNT_SID_, TWILIO_AUTH_TOKEN_)
        message = client.messages.create(
            from_=TWILIO_NUMBER_,
            messaging_service_sid="MG764153f5997679716afa983293b0a273",
            to=to_number,
            body=body,
        )

        return message
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return None


def fetchAndStoreMessage(message_sid, textmessage):

    try:
        client = Client(TWILIO_ACCOUNT_SID_, TWILIO_AUTH_TOKEN_)
        message = client.messages(message_sid).fetch()

        textmessage.to_country = message.to_country
        textmessage.to_state = message.to_state
        textmessage.sms_message_sid = message.sid
        textmessage.num_media = message.num_media
        textmessage.to_city = message.to_city
        textmessage.from_zip = message.from_zip
        textmessage.sms_sid = message.sid
        textmessage.from_state = message.from_state
        textmessage.sms_status = message.status
        textmessage.from_city = message.from_city
        textmessage.body = message.body
        textmessage.from_country = message.from_country
        textmessage.to_number = message.to
        textmessage.to_zip = message.to_zip
        textmessage.num_segments = message.num_segments
        textmessage.message_sid = message.sid
        textmessage.account_sid = message.account_sid
        textmessage.from_number = message.from_
        textmessage.api_version = message.api_version

        textmessage.save()
        return textmessage

    except Exception as e:
        logger.error(f"Error fetching message: {e}")
        return None


def getTextMessageBuildingSearchResponse(message_body):

    if not message_body:
        return None

    search_url = "http://127.0.0.1:8000/buildings/building"  # Adjust your search API URL accordingly
    params = {"search": message_body, "format": "json"}
    response = requests.get(search_url, params=params, timeout=10)
    buildings = response.json() if response.status_code == 200 else []
    return buildings.get("results", []) if buildings else []
