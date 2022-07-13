from rest_framework import serializers
from .models import Letter as LetterModel


class MainpageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LetterModel
        fields = ["letter_review", "category", "title", "content"]
