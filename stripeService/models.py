from django.db import models


class Customer(models.Model):
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    balance = models.IntegerField(default=0)
    created = models.DateTimeField()
    currency = models.CharField(max_length=10, null=True, blank=True)
    delinquent = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    invoice_prefix = models.CharField(max_length=50)
    livemode = models.BooleanField(default=False)
    next_invoice_sequence = models.IntegerField(default=1)
    tax_exempt = models.CharField(max_length=50, default="none")

    def __str__(self):
        return self.name if self.name else self.stripe_customer_id


class PaymentIntent(models.Model):
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, related_name="payment_intents"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_capturable = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10)
    status = models.CharField(max_length=50)  # e.g., succeeded, pending, failed
    created = models.DateTimeField()
    description = models.TextField(null=True, blank=True)
    capture_method = models.CharField(max_length=50)
    confirmation_method = models.CharField(max_length=50)
    livemode = models.BooleanField(default=False)

    def __str__(self):
        return self.stripe_payment_intent_id


class Subscription(models.Model):
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="subscriptions"
    )
    status = models.CharField(max_length=50)  # e.g., active, past_due, canceled
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    billing_cycle_anchor = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    collection_method = models.CharField(
        max_length=50
    )  # e.g., charge_automatically, send_invoice
    created = models.DateTimeField()
    currency = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)
    livemode = models.BooleanField(default=False)

    def __str__(self):
        return self.stripe_subscription_id


class Invoice(models.Model):
    stripe_invoice_id = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="invoices"
    )
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3)
    status = models.CharField(
        max_length=50
    )  # e.g., draft, open, paid, uncollectible, void
    created = models.DateTimeField()
    due_date = models.DateTimeField(
        null=True, blank=True
    )  # Not all invoices will have a due date
    description = models.TextField(null=True, blank=True)
    invoice_pdf = models.URLField(null=True, blank=True)  # URL to the invoice PDF
    customer_email = models.EmailField(null=True, blank=True)  # Email of the customer

    def __str__(self):
        return f"Invoice {self.stripe_invoice_id} for {self.customer_email}"


class StripeEvent(models.Model):
    stripe_event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=255, blank=True, null=True)
    processed_at = models.DateTimeField(auto_now_add=True)
