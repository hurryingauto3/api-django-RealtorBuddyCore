import logging
from rest_framework import serializers
from .models import Building, Cooperation, CooperationHistory

logger = logging.getLogger(__name__)

class CooperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooperation
        fields = ["cooperate", "cooperation_fixed", "cooperation_percentage"]

class CooperationHistorySerializer(serializers.ModelSerializer):
    cooperate = serializers.BooleanField(required=False, allow_null=True)
    class Meta:
        model = CooperationHistory
        fields = ['cooperate', 'cooperation_fixed', 'cooperation_percentage', 'updated_at']

class BuildingSerializer(serializers.ModelSerializer):
    cooperation = CooperationSerializer(required=False)  # Make the cooperation field optional

    class Meta:
        model = Building
        fields = [
            "id",
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
        ]

    def create(self, validated_data):
        cooperation_data = validated_data.pop('cooperation', None)
        building = Building.objects.create(**validated_data)
        if cooperation_data:
            Cooperation.objects.create(building=building, **cooperation_data)
        return building

    def update(self, instance, validated_data):
        cooperation_data = validated_data.pop('cooperation', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if cooperation_data:
            if hasattr(instance, 'cooperation'):
                for key, value in cooperation_data.items():
                    setattr(instance.cooperation, key, value)
                instance.cooperation.save()
            else:
                Cooperation.objects.create(building=instance, **cooperation_data)
        return instance