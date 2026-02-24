from rest_framework import serializers

from .models import Camera
from Apps.RegleSHE.models import HSERule
from Apps.RegleSHE.serializers import HSERuleSerializer



class CameraSerializer(serializers.ModelSerializer):
    hse_rules = HSERuleSerializer(many=True, read_only=True)

    class Meta:
        model  = Camera
        fields = [
            'id', 'name', 'location', 'stream_url',
            'status', 'is_active', 'created_at', 'updated_at',
            'hse_rules'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CameraCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Camera
        fields = ['name', 'location', 'stream_url']

    def validate_name(self, value):
        if Camera.objects.filter(name=value).exists():
            raise serializers.ValidationError("Une caméra avec ce nom existe déjà.")
        return value


class CameraUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Camera
        fields = ['name', 'location', 'stream_url', 'status', 'is_active']


class CameraStatusSerializer(serializers.ModelSerializer):
    """Serializer léger pour juste changer le statut"""
    class Meta:
        model  = Camera
        fields = ['status', 'is_active']