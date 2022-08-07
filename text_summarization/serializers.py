from rest_framework import serializers

from .models import text

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = text
        fields = '__all__'

class InputSerializer(serializers.ModelSerializer):
    class Meta:
        model = text
        fields = ['raw_text']