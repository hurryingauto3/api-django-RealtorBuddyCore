import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.twiml.messaging_response import MessagingResponse

@csrf_exempt
@require_POST
def textMessageBuildingSearch(request):
    message_body = request.POST.get('Body', '').strip()
    search_url = 'http://127.0.0.1:8000/buildings/api'  # Adjust your search API URL accordingly
    params = {'search': message_body}
    
    # Make a GET request to your search API
    response = requests.get(search_url, params=params, timeout=10)
    buildings = response.json() if response.status_code == 200 else []

    resp = MessagingResponse()
    msg = resp.message()

    if buildings:
        buildings_info = "\n\n".join([f"{b['name']}, {b['address']}, {b['city']}" for b in buildings])
        msg.body(f"Found buildings:\n\n{buildings_info}")
    else:
        msg.body("No buildings found matching your query.")

    return HttpResponse(str(resp), content_type="application/xml")
