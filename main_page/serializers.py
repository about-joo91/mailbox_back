from rest_framework import serializers

from user.models import User as UserModel

from .models import Letter as LetterModel
from .models import LetterReview as LetterReviewModel
from .models import LetterReviewLike as LetterreviewLikeModel


class LetterSerilaizer(serializers.ModelSerializer):
    def create(self, validated_data):
        new_letter = LetterModel.objects.create(**validated_data)
        new_letter.save()
        return new_letter

    class Meta:
        model = LetterModel
        fields = [
            "letter_author",
            "title",
            "content",
            "create_date",
            "worryboard",
        ]


class MainPageDataSerializer(serializers.ModelSerializer):
    rank_list = serializers.SerializerMethodField()
    user_profile_data = serializers.SerializerMethodField()

    def get_rank_list(self, obj):
        grade_in_order_user_list = UserModel.objects.select_related("userprofile").all().order_by("-monglegrade")[:10]
        rank_list = [
            {
                "username": rank_list.username,
                "profile_img": rank_list.userprofile.profile_img,
            }
            for rank_list in grade_in_order_user_list
        ]
        return rank_list

    def get_user_profile_data(self, obj):
        return {
            "grade": obj.monglegrade.grade,
            "profile_img": obj.userprofile.profile_img,
            "mongle_img": obj.monglegrade.mongle,
        }

    class Meta:
        model = UserModel
        fields = ["user_profile_data", "rank_list"]


class BestReviewSerializer(serializers.ModelSerializer):
    letter_review_like_id = serializers.SerializerMethodField()
    review_id = serializers.SerializerMethodField()

    def get_letter_review_like_id(self, obj):
        cur_user = self.context["request"].user
        try:
            return obj.letterreviewlike_set.get(user=cur_user, letter_review=obj).id
        except LetterreviewLikeModel.DoesNotExist:
            pass

    def get_review_id(self, obj):
        return obj.id

    class Meta:
        model = LetterReviewModel
        fields = [
            "like_count",
            "review_id",
            "letter_review_like_id",
            "content",
            "review_author",
            "grade",
            "create_date",
        ]


class LiveReviewSerializer(serializers.ModelSerializer):
    letter_review_like_id = serializers.SerializerMethodField()
    review_id = serializers.SerializerMethodField()

    def get_letter_review_like_id(self, obj):
        cur_user = self.context["request"].user
        try:
            return obj.letterreviewlike_set.get(user=cur_user, letter_review=obj).id
        except LetterreviewLikeModel.DoesNotExist:
            pass

    def get_review_id(self, obj):
        return obj.id

    class Meta:
        model = LetterReviewModel
        fields = [
            "like_count",
            "review_id",
            "letter_review_like_id",
            "content",
            "review_author",
            "grade",
            "create_date",
        ]
