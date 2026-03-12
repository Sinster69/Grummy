from rest_framework import serializers
from .models import DeliveryTask


class DeliveryTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryTask
        fields = "__all__"
        read_only_fields = ["restaurant"]

    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters")
        return value
