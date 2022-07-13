from rest_framework import serializers
from .models import LetterReview as LetterReviewModel


class MainpageSerializer(serializers.ModelSerializer):
    take_letter = serializers.SerializerMethodField()
    def get_take_letter(self,obj):
        print(dir(obj))
        a= obj.userlettertargetuser_set.all()
        print(a)
        return "ttt"
    class Meta:



        model = LetterReviewModel
        fields = ["take_letter","review_author", "letter", "grade", "content"]
        extra_kwargs = {
            "review_author": {"read_only": True},
            "letter": {"read_only": True},
            "grade": {"read_only": True},
            "content": {"read_only": True},
        }
