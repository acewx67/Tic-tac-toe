from rest_framework import serializers
from .models import Array
class ArraySerializer(serializers.Serializer):
    data = serializers.JSONField(default=[None]*9)
    group_name = serializers.CharField(max_length=255)
    def create(self,validated_data):
        return Array.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.data = validated_data.get('data',instance.data)
        instance.save()
        return instance