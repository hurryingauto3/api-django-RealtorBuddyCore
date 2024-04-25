from django.db import models

class Customer(models.Model):
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

class PaymentMethod(models.Model):
    stripe_payment_method_id = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField(max_length=50)  # e.g., card
    last4 = models.CharField(max_length=4, null=True, blank=True)
    exp_month = models.IntegerField(null=True, blank=True)
    exp_year = models.IntegerField(null=True, blank=True)
    brand = models.CharField(max_length=50, null=True, blank=True)  # e.g., Visa, Mastercard

class PaymentIntent(models.Model):
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='payment_intents')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=50)  # e.g., succeeded, pending, failed
    created = models.DateTimeField()
    description = models.TextField(null=True, blank=True)

class RecurringPayment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='recurring_payments')
    payment_intent = models.ForeignKey(PaymentIntent, on_delete=models.CASCADE, related_name='recurring_details')
    interval = models.CharField(max_length=50)  # e.g., monthly, yearly
    next_payment_due = models.DateTimeField()
