# serializers.py
from rest_framework import serializers
from .models import Building

class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = '__all__'  # Adjust fields as needed
