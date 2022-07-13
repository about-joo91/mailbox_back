from rest_framework import serializers
from .models import LetterReview as LetterReviewModel


class MainpageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LetterReviewModel
        fields = ["review_author", "letter", "grade", "content"]
        extra_kwargs = {
            "review_author": {"read_only": True},
            "letter": {"read_only": True},
            "grade": {"read_only": True},
            "content": {"read_only": True},
        }
