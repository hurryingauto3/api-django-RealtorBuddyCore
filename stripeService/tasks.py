import datetime
import stripe
from .models import Customer, PaymentMethod, PaymentIntent
from decimal import Decimal
from celery import shared_task


@shared_task(name="handlePaymentIntentEvent", queue="stripeService")
def handlePaymentIntentEvent(payment_intent):
    # Convert Stripe timestamp to datetime
    created_datetime = datetime.datetime.fromtimestamp(payment_intent["created"])

    # Retrieve or create the customer
    customer = stripe.Customer(id=payment_intent["customer"]).retrieve()
    customer, _ = Customer.objects.get_or_create(
        stripe_customer_id=customer["id"],
        defaults={
            "name": customer["name"],
            "email": customer["email"],
            "phone": customer["phone"] if "phone" in customer else "",
        },  # You might want to update these fields properly based on your model
    )

    # Retrieve or create the payment method
    payment_method = stripe.PaymentMethod.retrieve(payment_intent["payment_method"])
    payment_method, _ = PaymentMethod.objects.get_or_create(
        stripe_payment_method_id=payment_method["id"],
        defaults={
            "customer": customer,
            "type": payment_method["type"],
            "last4": payment_method["card"]["last4"],
            "exp_month": payment_method["card"]["exp_month"],
            "exp_year": payment_method["card"]["exp_year"],
            "brand": payment_method["card"]["brand"],
        },  # You might want to update these fields properly based on your model
    )

    # Create the payment intent record
    PaymentIntent.objects.create(
        stripe_payment_intent_id=payment_intent["id"],
        customer=customer,
        payment_method=payment_method,
        amount=Decimal(payment_intent["amount"] / 100),  # Stripe amounts are in cents
        amount_received=Decimal(payment_intent["amount_received"] / 100),
        currency=payment_intent["currency"],
        status=payment_intent["status"],
        created=created_datetime,
        description=payment_intent.get("description", ""),
    )
