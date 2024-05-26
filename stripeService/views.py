import logging
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from .tasks import (
    handleCustomerEvent,
    handleInvoiceEvent,
    handlePaymentIntentEvent,
    handleSubscriptionEvent,
)
from .models import StripeEvent  # This would be a new model to track processed events
from APIRealtorBuddyCore.config import STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET

logger = logging.getLogger(__name__)
stripe.api_key = STRIPE_API_KEY


@csrf_exempt
@require_POST
def stripeEventHandler(request):
    event = None
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    # Check if the event has already been processed
    if StripeEvent.objects.filter(stripe_event_id=event["id"]).exists():
        logger.info(f"Duplicate event {event['id']} skipped")
        return HttpResponse(status=200)

    # Handling different types of events
    with transaction.atomic():
        # Mark event as handled to prevent duplicate processing
        StripeEvent.objects.create(
            stripe_event_id=event["id"], event_type=event["type"]
        )

        if "payment_intent" in event["type"]:
            try:
                handlePaymentIntentEvent(event)
                return HttpResponse(status=200)
            except Exception as e:
                logger.error(f"Error processing payment_intent event: {e}")
                return HttpResponse(status=400)

        if "subscription" in event["type"]:
            try:
                handleSubscriptionEvent(event)
                return HttpResponse(status=200)
            except Exception as e:
                logger.error(f"Error processing subscription event: {e}")
                return HttpResponse(status=400)

        if "customer" in event["type"]:
            try:
                handleCustomerEvent(event)
                return HttpResponse(status=200)
            except Exception as e:
                logger.error(f"Error processing customer event: {e}")
                return HttpResponse(status=400)

        if "invoice" in event["type"]:
            try:
                handleInvoiceEvent(event)
                return HttpResponse(status=200)
            except Exception as e:
                logger.error(f"Error processing invoice event: {e}")
                return HttpResponse(status=400)

    logger.info("Unhandled event: %s", event["type"])
    return HttpResponse(status=200)
