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
        grade_in_order_user_list = (
            UserModel.objects.select_related("userprofile")
            .all()
            .order_by("-monglegrade")[:10]
        )
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
            "grade": obj.userprofile.mongle_grade,
            "profile_img": obj.userprofile.profile_img,
        }

    class Meta:
        model = UserModel
        fields = ["user_profile_data", "rank_list"]


class BestReviewSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    review_id = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    def get_is_liked(self, obj):
        cur_user = self.context["request"].user

        return LetterreviewLikeModel.objects.filter(
            user=cur_user, letter_review=obj
        ).exists()

    def get_review_id(self, obj):
        return obj.id

    def get_like_count(self, obj):
        return obj.letterreviewlike_set.filter(letter_review=obj).count()

    class Meta:
        model = LetterReviewModel
        fields = [
            "like_count",
            "review_id",
            "is_liked",
            "content",
            "review_author",
            "grade",
            "create_date",
        ]


class LiveReviewSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    review_id = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    def get_is_liked(self, obj):
        cur_user = self.context["request"].user
        return LetterreviewLikeModel.objects.filter(
            user=cur_user, letter_review=obj
        ).exists()

    def get_review_id(self, obj):
        return obj.id

    def get_like_count(self, obj):
        return obj.letterreviewlike_set.filter(letter_review=obj).count()

    class Meta:
        model = LetterReviewModel
        fields = [
            "like_count",
            "review_id",
            "is_liked",
            "content",
            "review_author",
            "grade",
            "create_date",
        ]
