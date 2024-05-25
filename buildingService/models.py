import re
import uuid
from django.db.models import F
from django.db import models
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

def advanced_common_forms(abbreviation_mapping, part):
    for i in abbreviation_mapping.keys():
        if part in abbreviation_mapping[i]:
            return abbreviation_mapping[i]

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

    state_codes = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    # Convert address to lowercase and remove all punctuation except spaces

    address = address.lower()
    address = address.split("#")[0]
    address = address.split("unit")[0]
    # Remove everything except alphanumeric characters and spaces, hyphens, slashes, and ampersands
    address = re.sub(r"[^a-z0-9\s\-/&]", "", address)

    # Replace multiple spaces with a single space
    address = re.sub(r"\s+", " ", address)

    # Split the address into parts
    address_parts = address.split()

    # Normalize the address parts based on the abbreviation mapping
    normalized_parts = []
    last_suffix_place = None
    last_part_is_suffix = False
    for i, part in enumerate(address_parts):

        # Look up the part in the abbreviation mapping
        common_forms = abbreviation_mapping.get(part)
        if not common_forms:
            common_forms = advanced_common_forms(abbreviation_mapping, part)
        
        if common_forms:
            last_suffix_place = i
            last_part_is_suffix = True
            
        else:
            last_part_is_suffix = False
        # Replace with the abbreviation if it exists, otherwise keep the original part
        normalized_part = common_forms[0] if common_forms else part

        if normalized_part.upper() in state_codes:
            break

        normalized_parts.append(normalized_part)

    # Re-join the normalized parts into a single string
    # Return the normalized address, stripping any leading/trailing whitespace
    if not last_part_is_suffix:
        if last_suffix_place:
            # if normalized_parts[last_suffix_place] in ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]:
            
            #     normalized_parts = normalized_parts[:last_suffix_place + 2]
            # else:
            normalized_parts = normalized_parts[:last_suffix_place + 1]
    if len(normalized_parts) < 2:
        return None

    normalized_address = " ".join(normalized_parts)    
    return normalized_address.strip()

def clean_name(name):

    # Convert name to lowercase and remove all punctuation except spaces
    name = re.sub(r"[^\w\s]", "", name.lower())

    # Replace multiple spaces with a single space
    name = re.sub(r"\s+", " ", name)
    name = name.split(",")[0]
    name = name.split("#")[0]
    name = name.split("unit")[0]

    name_parts = name.split(" ")
    clean_parts = []

    for part in name_parts:
        clean_parts.append(part[0].upper() + part[1:])

    name = " ".join(clean_parts)
    return name

class Building(models.Model):

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(editable=False, unique=True, null=False)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.TextField(null=False, blank=False)
    address = models.TextField(null=False, blank=False)
    address_normalized = models.TextField(editable=False, null=False, blank=False)
    neighborhood = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
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
        self.phone_normalized = normalize_phone_number(self.phone)
        self.address_normalized = normalize_address(self.address)
        if not self.pk and not self.uuid:  # Check if new and UUID not set
            self.uuid = (
                uuid.uuid5(uuid.NAMESPACE_DNS, self.address_normalized)
                if self.address_normalized
                else None
            )
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
    updated_at = models.DateTimeField(auto_now=True)
    # building = models.ForeignKey(
    #     Building, on_delete=models.CASCADE, related_name="cooperation"
    # )
    building = models.OneToOneField(Building, on_delete=models.CASCADE, related_name='cooperation')
    # title = models.TextField(null=True, blank=True)
    cooperate = models.BooleanField(default=False, null=True, blank=True)
    cooperation_fixed = models.IntegerField(null=True, blank=True)
    cooperation_percentage = models.IntegerField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.pk is not None:  # Checks if the instance already exists
            CooperationHistory.objects.create(
                cooperation=self,
                cooperate=self.cooperate,
                cooperation_fixed=self.cooperation_fixed,
                cooperation_percentage=self.cooperation_percentage
            )
        super().save(*args, **kwargs)
    
class CooperationHistory(models.Model):
    id = models.AutoField(primary_key=True)
    cooperation = models.ForeignKey(Cooperation, on_delete=models.CASCADE, related_name='history')
    updated_at = models.DateTimeField(auto_now_add=True)
    cooperate = models.BooleanField(default=False)
    cooperation_fixed = models.IntegerField(null=True, blank=True)
    cooperation_percentage = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']  # Orders the history entries by most recent

    def __str__(self):
        return f"History for {self.cooperation} at {self.updated_at}"
