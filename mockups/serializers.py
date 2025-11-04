from rest_framework import serializers
from .models import Mockup

class MockupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mockup
        fields = ['id', 'text', 'font', 'text_color', 'shirt_color', 'image', 'created_at']