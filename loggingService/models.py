from django.db import models

class CloudFlareLog(models.Model):
    
    timestamp = models.DateTimeField()
    url = models.URLField()
    method = models.CharField(max_length=10)
    headers = models.JSONField()
    cf = models.JSONField()

    def __str__(self):
        return f"{self.timestamp} - {self.url}"
