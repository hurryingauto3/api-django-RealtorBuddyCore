import requests
from APIRealtorBuddyCore.config import (
    TWILIO_ACCOUNT_SID_,
    TWILIO_AUTH_TOKEN_,
    TWILIO_NUMBER_,
)
from twilio.rest import Client


def sendTextMessage(to_number, body):
    client = Client(TWILIO_ACCOUNT_SID_, TWILIO_AUTH_TOKEN_)

    message = client.messages.create(
        from_=TWILIO_NUMBER_,
        to=to_number,
        body=body,
    )

    return message


def getTextMessageBuildingSearchResponse(message_body):
    
    if not message_body:
        return None

    search_url = (
        "http://127.0.0.1:8000/buildings/api"  # Adjust your search API URL accordingly
    )
    params = {"search": message_body, "format": "json"}
    response = requests.get(search_url, params=params, timeout=10)
    buildings = response.json() if response.status_code == 200 else []
    return buildings
