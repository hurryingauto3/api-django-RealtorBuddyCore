import re
import uuid
from django.db import models
from django.db.models import F
from django.utils.timezone import now
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


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


def normalize_phone_number(phone):
    # Remove any non-digit characters from the phone number
    phone = re.sub(r"\D", "", str(phone))

    # Check if the phone number starts with '1' and remove it if present
    if phone.startswith("1"):
        phone = phone[1:]

    # Pad the phone number with zeros if it's less than 10 digits
    phone = phone.zfill(10)

    # Format the phone number as (XXX) XXX-XXXX
    formatted_phone = f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"

    return formatted_phone


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

def clean_name(name):
    
    # Convert name to lowercase and remove all punctuation except spaces
    name = re.sub(r"[^\w\s]", "", name.lower())

    # Replace multiple spaces with a single space
    name = re.sub(r"\s+", " ", name)
    name = name.split(',')[0]
    name = name.split('#')[0]
    name = name.split('unit')[0]

    name_parts = name.split(' ')
    clean_parts = []
    
    for part in name_parts:
        clean_parts.append(part[0].upper() + part[1:])
    
    name = ' '.join(clean_parts)
    return name

class Building(models.Model):

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
    phone_normalized = models.TextField(editable=False, blank=True, null=True)
    website = models.TextField(blank=True, null=True)
    # search_vector = models.SearchVectorField(null=True)

    def save(self, *args, **kwargs):
        self.name = clean_name(self.name)
        self.address_normalized = normalize_address(self.address)
        self.phone_normalized = normalize_phone_number(self.phone)
        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, self.address_normalized)
        super(Building, self).save(*args, **kwargs)  # Save all changes first

        # Now update the search vector
        # vector = SearchVector('name', weight='A') + SearchVector('address_normalized', weight='B')
        # Building.objects.filter(pk=self.pk).update(search_vector=vector)

    # company_name = models.TextField(blank=True, null=True)
    # min_lease_term = models.IntegerField(blank=True, null=True)
    # year_built = models.IntegerField(blank=True, null=True)
    # year_renovated = models.IntegerField(blank=True, null=True)
    # n_units = models.IntegerField(blank=True, null=True)
    # n_floors = models.IntegerField(blank=True, null=True)


class Cooperation(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(default=now)
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="cooperation"
    )
    title = models.TextField(null=True, blank=True)
    cooperate = models.BooleanField(default=False, null=True, blank=True)
    cooperation_fixed = models.IntegerField(null=True, blank=True)
    cooperation_percentage = models.IntegerField(null=True, blank=True)
