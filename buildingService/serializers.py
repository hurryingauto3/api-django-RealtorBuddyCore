# serializers.py
from rest_framework import serializers
from .models import Building, Cooperation


class CooperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooperation
        fields = ["title", "cooperate", "cooperation_fixed", "cooperation_percentage"]


class BuildingSerializer(serializers.ModelSerializer):
    cooperation = CooperationSerializer(many=True, read_only=True)  # Ensure 'many=True' is set

    class Meta:
        model = Building
        fields = [
            "name",
            "created_at",
            "updated_at",
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
            "cooperation",
            # "company_name",
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
