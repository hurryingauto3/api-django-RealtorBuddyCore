
import json
import logging
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from APIRealtorBuddyCore.config import STRIPE_API_KEY

from .tasks import handlePaymentIntentEvent

logger = logging.getLogger(__name__)
stripe.api_key = STRIPE_API_KEY

# Using Django
@csrf_exempt
@require_POST
def stripeEventHandler(request):
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except ValueError as e:
        logger.error("Error while parsing webhook payload: %s", e)
        return HttpResponse(status=400)

    # Handle the event
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        logger.info("PaymentIntent was successful!")
        handlePaymentIntentEvent.delay(payment_intent)

    return HttpResponse(status=200)
