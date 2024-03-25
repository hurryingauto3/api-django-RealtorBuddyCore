from django.db import models

# Create your models here.
class TextMessage(models.Model):
    id = models.AutoField(primary_key=True)
    sid = models.CharField(max_length=100, unique=True)  # SID should be unique
    body = models.TextField()
    num_segments = models.CharField(max_length=10)
    direction = models.CharField(max_length=20)
    from_number = models.CharField(max_length=30, db_index=True)  # 'from' is a reserved keyword, hence '_number' is used
    to_number = models.CharField(max_length=30, db_index=True)
    date_updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    uri = models.URLField(max_length=200)
    account_sid = models.CharField(max_length=50)
    num_media = models.CharField(max_length=10)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=20)
    date_sent = models.DateTimeField(null=True, blank=True)
    messaging_service_sid = models.CharField(max_length=50, null=True, blank=True)
    error_code = models.IntegerField(null=True, blank=True)
    price_unit = models.CharField(max_length=10, null=True, blank=True)
    api_version = models.CharField(max_length=20, null=True, blank=True)
    subresource_uris = models.JSONField(null=True, blank=True)

class WhatsAppMessage(models.Model):
    id = models.AutoField(primary_key=True)
    sms_message_sid = models.CharField(max_length=34, unique=True, null=True, blank=True)  # Optional
    sms_sid = models.CharField(max_length=34, null=True, blank=True)  # Optional
    wa_id = models.CharField(max_length=20, null=True, blank=True)  # Optional
    num_media = models.CharField(max_length=3, blank=True, null=True)  # Optional
    profile_name = models.CharField(max_length=100, blank=True, null=True)  # Optional
    message_type = models.CharField(max_length=10, blank=True, null=True)  # Optional
    sms_status = models.CharField(max_length=20, blank=True, null=True)  # Optional
    body = models.TextField(blank=True, null=True)  # Optional
    to_number = models.CharField(max_length=30)  # Twilio WhatsApp number
    from_number = models.CharField(max_length=30)  # Sender's WhatsApp number
    num_segments = models.CharField(max_length=3, blank=True, null=True)  # Optional
    referral_num_media = models.CharField(max_length=3, blank=True, null=True)  # Optional
    message_sid = models.CharField(max_length=34, blank=True, null=True)  # Optional
    account_sid = models.CharField(max_length=34, blank=True, null=True)  # Optional
    api_version = models.CharField(max_length=10, blank=True, null=True)  # Optional
