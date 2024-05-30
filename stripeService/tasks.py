import logging
import datetime

from django.utils import timezone
from decimal import Decimal

from twilioService.utils import sendTextMessage
from .models import Customer, PaymentIntent, Subscription, Invoice
from decimal import Decimal
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name="handlePaymentIntentEvent")
def handlePaymentIntentEvent(event):
    """
    Handles the payment intent event such as payment_intent.succeeded, payment_intent.created, payment_intent.canceled, etc.
    Args:
        event (dict): The Stripe event data
    """
    payment_intent_data = event["data"]["object"]

    customer_id = payment_intent_data.get("customer")
    customer = None
    if customer_id:
        customer, _ = Customer.objects.get_or_create(
            stripe_customer_id=customer_id,
            defaults={
                "name": None,
                "email": None,
                "phone": None,
                "balance": 0,
                "created": datetime.datetime.fromtimestamp(
                    payment_intent_data["created"]
                ),
                "currency": None,
                "delinquent": False,
                "description": None,
                "invoice_prefix": "",
                "livemode": False,
                "next_invoice_sequence": 1,
                "tax_exempt": "none",
            },
        )

    PaymentIntent.objects.update_or_create(
        stripe_payment_intent_id=payment_intent_data["id"],
        defaults={
            "customer": customer,
            "amount": payment_intent_data["amount"] / 100,  # Convert from cents
            "amount_capturable": payment_intent_data["amount_capturable"] / 100,
            "amount_received": payment_intent_data["amount_received"] / 100,
            "currency": payment_intent_data["currency"],
            "status": payment_intent_data["status"],
            "created": datetime.datetime.fromtimestamp(payment_intent_data["created"]),
            "description": payment_intent_data.get("description"),
            "capture_method": payment_intent_data["capture_method"],
            "confirmation_method": payment_intent_data["confirmation_method"],
            "livemode": payment_intent_data["livemode"],
        },
    )


@shared_task(name="handleCustomerEvent")
def handleCustomerEvent(event):
    """
    Handles the customer event such as customer.created, customer.updated.
    Args:
        event (dict): The Stripe event data
    """

    customer_data = event["data"]["object"]
    Customer.objects.update_or_create(
        stripe_customer_id=customer_data["id"],
        defaults={
            "name": customer_data.get("name"),
            "email": customer_data.get("email"),
            "phone": customer_data.get("phone"),
            "balance": customer_data["balance"],
            "created": datetime.datetime.fromtimestamp(customer_data["created"]),
            "currency": customer_data.get("currency"),
            "delinquent": customer_data["delinquent"],
            "description": customer_data.get("description"),
            "invoice_prefix": customer_data["invoice_prefix"],
            "livemode": customer_data["livemode"],
            "next_invoice_sequence": customer_data["next_invoice_sequence"],
            "tax_exempt": customer_data["tax_exempt"],
        },
    )


@shared_task(name="handleInvoiceEvent")
def handleInvoiceEvent(event):
    """
    Handles the invoice event such as invoice.created, invoice.updated, invoice.payment_succeeded, etc.
    Args:
        event (dict): The Stripe event data
    """
    invoice_data = event["data"]["object"]
    # Convert Stripe timestamp to datetime
    created_datetime = timezone.make_aware(
        datetime.datetime.fromtimestamp(invoice_data["created"])
    )

    due_datetime = None
    if invoice_data.get("due_date"):
        due_datetime = timezone.make_aware(
            datetime.datetime.fromtimestamp(invoice_data["due_date"])
        )

    invoice, created = Invoice.objects.update_or_create(
        stripe_invoice_id=invoice_data["id"],
        defaults={
            "customer": Customer.objects.get(
                stripe_customer_id=invoice_data["customer"]
            ),
            "amount_due": Decimal(invoice_data["amount_due"])
            / 100,  # Assuming amount is in cents
            "amount_paid": Decimal(invoice_data["amount_paid"]) / 100,
            "currency": invoice_data["currency"],
            "status": invoice_data["status"],
            "created": created_datetime,
            "due_date": due_datetime,
            "description": invoice_data.get("description"),
            "invoice_pdf": invoice_data.get("invoice_pdf"),
            "customer_email": invoice_data["customer_email"],
        },
    )

    if invoice_data["status"] == "paid" and created:
        # Send a text message to the customer
        sendTextMessage(
            to_number=invoice.customer.phone,
            body=f"Your payment of {invoice.amount_due} {invoice.currency.upper()} has been received. Thank you for subscribing Realtor Buddy.",
        )
        
    if invoice_data["status"] == "open" and created:
        # Send a text message to the customer
        sendTextMessage(
            to_number=invoice.customer.phone,
            body=f"Your payment of {invoice.amount_due} {invoice.currency.upper()} is due. Please pay at your earliest convenience to avoid service interruption.",
        )
    
    if invoice_data["status"] == "past_due" and created:
        # Send a text message to the customer
        sendTextMessage(
            to_number=invoice.customer.phone,
            body=f"Your payment of {invoice.amount_due} {invoice.currency.upper()} is past due. Please pay immediately to avoid service interruption.",
        )
        

@shared_task(name="handleSubscriptionEvent")
def handleSubscriptionEvent(event):
    """
    Handles the subscription event such as customer.subscription.created, customer.subscription.updated, etc.
    Args:
        event (dict): The Stripe event data
    """
    subscription_data = event["data"]["object"]
    customer_id = subscription_data.get("customer")
    customer = None
    if customer_id:
        customer, _ = Customer.objects.get_or_create(
            stripe_customer_id=customer_id,
            defaults={
                "name": None,
                "email": None,
                "phone": None,
                "balance": 0,
                "created": datetime.datetime.fromtimestamp(
                    subscription_data["created"]
                ),
                "currency": None,
                "delinquent": False,
                "description": None,
                "invoice_prefix": "",
                "livemode": False,
                "next_invoice_sequence": 1,
                "tax_exempt": "none",
            },
        )

    Subscription.objects.update_or_create(
        stripe_subscription_id=subscription_data["id"],
        defaults={
            "customer": customer,
            "status": subscription_data["status"],
            "current_period_start": datetime.datetime.fromtimestamp(
                subscription_data["current_period_start"]
            ),
            "current_period_end": datetime.datetime.fromtimestamp(
                subscription_data["current_period_end"]
            ),
            "billing_cycle_anchor": datetime.datetime.fromtimestamp(
                subscription_data["billing_cycle_anchor"]
            ),
            "cancel_at_period_end": subscription_data["cancel_at_period_end"],
            "canceled_at": (
                datetime.datetime.fromtimestamp(subscription_data["canceled_at"])
                if subscription_data["canceled_at"]
                else None
            ),
            "collection_method": subscription_data["collection_method"],
            "created": datetime.datetime.fromtimestamp(subscription_data["created"]),
            "currency": subscription_data["currency"],
            "description": subscription_data.get("description"),
            "livemode": subscription_data["livemode"],
        },
    )
