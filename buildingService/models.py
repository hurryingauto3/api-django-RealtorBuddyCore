from django.db import models

# Django's UUID support
import uuid

# For handling TIMESTAMP, Django uses DateTimeField
from django.utils.timezone import now

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=now)
    name = models.TextField()

class Building(models.Model):
    
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.TextField()
    address = models.TextField()
    address_normalized = models.TextField()
    neighborhood = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    min_lease_term = models.IntegerField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)
    year_built = models.IntegerField(blank=True, null=True)
    year_renovated = models.IntegerField(blank=True, null=True)
    n_units = models.IntegerField(blank=True, null=True)
    n_floors = models.IntegerField(blank=True, null=True)

class Cooperation(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=now)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    cooperate = models.BooleanField()
    cooperation_type = models.TextField()
    value = models.IntegerField()