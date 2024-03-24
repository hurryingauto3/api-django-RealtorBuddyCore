import requests
from twilio.twiml.messaging_response import MessagingResponse

def getTextMessageBuildingSearchResponse(message_body):
    
    search_url = 'http://127.0.0.1:8000/buildings/api'  # Adjust your search API URL accordingly
    params = {'search': message_body}
    response = requests.get(search_url, params=params, timeout=10)
    buildings = response.json() if response.status_code == 200 else []

    resp = MessagingResponse()
    msg = resp.message()

    if buildings:
        buildings_info = "\n\n".join([f"{b['name']}, {b['address']}, {b['city']}" for b in buildings])
        msg.body(f"Found buildings:\n\n{buildings_info}")
    else:
        msg.body("No buildings found matching your query.")

    return resp