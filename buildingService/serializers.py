import logging
from rest_framework import serializers
from .models import Building, Cooperation, CooperationHistory

logger = logging.getLogger(__name__)

class CooperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cooperation
        fields = ["cooperate", "cooperation_fixed", "cooperation_percentage"]

class CooperationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CooperationHistory
        fields = ['cooperate', 'cooperation_fixed', 'cooperation_percentage', 'updated_at']

class BuildingSerializer(serializers.ModelSerializer):
    cooperation = CooperationSerializer()  # Removed 'many=False' as it's the default for one-to-one

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
        cooperation_data = validated_data.pop('cooperation', None)  # Changed from list to single object handling
        building = Building.objects.create(**validated_data)
        if cooperation_data:
            Cooperation.objects.create(building=building, **cooperation_data)
        return building
    
    def update(self, instance, validated_data):
        cooperation_data = validated_data.pop('cooperation', None)

        # Update the main Building instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle the Cooperation instance
        if cooperation_data:
            if hasattr(instance, 'cooperation'):
                # Update existing Cooperation instance
                for key, value in cooperation_data.items():
                    setattr(instance.cooperation, key, value)
                instance.cooperation.save()
                logger.info("Updated existing Cooperation instance for building with id %s and cooperation id %s", instance.id, instance.cooperation.id)
            else:
                # Create new Cooperation instance if it does not exist
                Cooperation.objects.create(building=instance, **cooperation_data)
                logger.info("Created Cooperation instance for building with id %s and cooperation id %s", instance.id, instance.cooperation.id)

        return instance