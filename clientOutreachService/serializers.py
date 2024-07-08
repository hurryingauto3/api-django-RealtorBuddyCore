from rest_framework import serializers
from .models import clientEmailDefinition, clientEmailOutReachRuleset, client

class ClientEmailDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = clientEmailDefinition
        fields = '__all__'  # Or list specific fields like ['id', 'email_subject', 'email_body']

class ClientEmailOutReachRulesetSerializer(serializers.ModelSerializer):
    class Meta:
        model = clientEmailOutReachRuleset
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = client
        fields = '__all__'