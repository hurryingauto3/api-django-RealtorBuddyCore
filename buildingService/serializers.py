# serializers.py
from rest_framework import serializers
from .models import Building, Cooperation


class CooperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooperation
        fields = ["title", "cooperate", "fixed", "value"]


class BuildingSerializer(serializers.ModelSerializer):
    cooperation = CooperationSerializer(required=False)

    class Meta:
        model = Building
        fields = [
            "name",
            "address",
            "neighborhood",
            "city",
            "state",
            "zip",
            "latitude",
            "longitude",
            "description",
            "phone",
            "website",
            "company_name",
            "cooperation"
            # "min_lease_term",
            # "year_built",
            # "year_renovated",
            # "n_units",
            # "n_floors",
        ]  # Include all the fields you need

    def create(self, validated_data):
        cooperation_data = validated_data.pop("cooperation", None)
        building = Building.objects.create(**validated_data)

        if cooperation_data:
            Cooperation.objects.create(building=building, **cooperation_data)

        return building
