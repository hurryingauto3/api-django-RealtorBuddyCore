from django.db import models
# Create your models here.
class TextMessage(models.Model):
    id = models.AutoField(primary_key=True)
    message_sid = models.CharField(max_length=34, blank=True, null=True, unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    to_country = models.CharField(max_length=10, blank=True, null=True)
    to_state = models.CharField(max_length=10, blank=True, null=True)
    num_media = models.CharField(max_length=3, blank=True, null=True)
    to_city = models.CharField(max_length=50, blank=True, null=True)
    from_zip = models.CharField(max_length=10, blank=True, null=True)
    from_state = models.CharField(max_length=10, blank=True, null=True)
    sms_status = models.CharField(max_length=20, blank=True, null=True)
    from_city = models.CharField(max_length=50, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    from_country = models.CharField(max_length=10, blank=True, null=True)
    to_number = models.CharField(max_length=30)
    message_service_sid = models.CharField(max_length=34, blank=True, null=True)
    to_zip = models.CharField(max_length=10, blank=True, null=True)
    num_segments = models.CharField(max_length=3, blank=True, null=True)
    account_sid = models.CharField(max_length=34, blank=True, null=True)
    from_number = models.CharField(max_length=30)
    api_version = models.CharField(max_length=10, blank=True, null=True)


# class WhatsAppMessage(models.Model):
#     id = models.AutoField(primary_key=True)
#     sms_message_sid = models.CharField(max_length=34, unique=True, null=True, blank=True)  # Optional
#     sms_sid = models.CharField(max_length=34, null=True, blank=True)  # Optional
#     wa_id = models.CharField(max_length=20, null=True, blank=True)  # Optional
#     num_media = models.CharField(max_length=3, blank=True, null=True)  # Optional
#     profile_name = models.CharField(max_length=100, blank=True, null=True)  # Optional
#     message_type = models.CharField(max_length=10, blank=True, null=True)  # Optional
#     sms_status = models.CharField(max_length=20, blank=True, null=True)  # Optional
#     body = models.TextField(blank=True, null=True)  # Optional
#     to_number = models.CharField(max_length=30)  # Twilio WhatsApp number
#     from_number = models.CharField(max_length=30)  # Sender's WhatsApp number
#     num_segments = models.CharField(max_length=3, blank=True, null=True)  # Optional
#     referral_num_media = models.CharField(max_length=3, blank=True, null=True)  # Optional
#     message_sid = models.CharField(max_length=34, blank=True, null=True)  # Optional
#     account_sid = models.CharField(max_length=34, blank=True, null=True)  # Optional
#     api_version = models.CharField(max_length=10, blank=True, null=True)  # Optional
