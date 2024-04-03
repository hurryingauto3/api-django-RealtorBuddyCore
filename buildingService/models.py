import re
import uuid
from django.db import models
from django.db.models import F
from django.utils.timezone import now
class AddressAbbreviation(models.Model):
    primary_key = models.AutoField(primary_key=True)
    standard_abbreviation = models.CharField(max_length=10, unique=True)
    common_forms = models.TextField()
    
    @classmethod
    def update_abbreviations(cls, abbr_dict):
        for standard, commons in abbr_dict.items():
            obj, created = cls.objects.update_or_create(
                standard_abbreviation=standard,
                defaults={"common_forms": ",".join(commons)},
            )

def normalize_address(address):
    # Fetch abbreviation mapping from the database and store it in a dictionary
    abbreviation_dict = (
        AddressAbbreviation.objects.annotate(common=F("common_forms"))
        .values_list("standard_abbreviation", "common")
        .order_by("standard_abbreviation")
    )
    abbreviation_mapping = {
        standard: common.split(",") for standard, common in abbreviation_dict
    }

    # Convert address to lowercase and remove all punctuation except spaces
    address = re.sub(r"[^\w\s]", "", address.lower())

    # Replace multiple spaces with a single space
    address = re.sub(r"\s+", " ", address)

    # Split the address into parts
    address_parts = address.split()

    # Normalize the address parts based on the abbreviation mapping
    normalized_parts = []
    for part in address_parts:
        # Look up the part in the abbreviation mapping
        common_forms = abbreviation_mapping.get(part)
        # Replace with the abbreviation if it exists, otherwise keep the original part
        normalized_part = common_forms[0] if common_forms else part
        normalized_parts.append(normalized_part)

    # Re-join the normalized parts into a single string
    normalized_address = " ".join(normalized_parts)
    # Return the normalized address, stripping any leading/trailing whitespace
    return normalized_address.strip()
class Building(models.Model):

    def save(self, *args, **kwargs):
        # Normalize the address and assign it to address_normalized
        self.address_normalized = normalize_address(self.address)
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, self.address_normalized)
        super(Building, self).save(*args, **kwargs)

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.TextField()
    address = models.TextField()
    address_normalized = models.TextField(editable=False)
    neighborhood = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    # company_name = models.TextField(blank=True, null=True)
    # min_lease_term = models.IntegerField(blank=True, null=True)
    # year_built = models.IntegerField(blank=True, null=True)
    # year_renovated = models.IntegerField(blank=True, null=True)
    # n_units = models.IntegerField(blank=True, null=True)
    # n_floors = models.IntegerField(blank=True, null=True)

class Cooperation(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=now)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='cooperations')
    title = models.TextField(null=True, blank=True)
    cooperate = models.BooleanField(default=False, null=True, blank=True)
    fixed = models.BooleanField(default=False, null=True, blank=True)
    value = models.IntegerField()
