from rest_framework import serializers
from .models import push
class pushSerializer(serializers.ModelSerializer):
    class Meta:
        model = push
        fields = ["id", "user", "endpoint", "description", "json_file", "workers", "status", "created"]