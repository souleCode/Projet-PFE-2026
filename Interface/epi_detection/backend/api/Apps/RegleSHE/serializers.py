from rest_framework import serializers
from .models import HSERule

class EpiCriticiteSerializer(serializers.Serializer):
    epi = serializers.CharField()
    criticite = serializers.CharField()

class HSERuleSerializer(serializers.ModelSerializer):
    epi_criticites = EpiCriticiteSerializer(many=True, required=False)

    class Meta:
        model = HSERule
        fields = '__all__'