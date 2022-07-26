from rest_framework import serializers

from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel

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
        user_profile_get = (
            UserModel.objects.select_related("userprofile")
            .all()
            .order_by("-monglegrade")[:10]
        )
        rank_list = [
            {
                "username": rank_list.username,
                "profile_img": rank_list.userprofile.profile_img,
            }
            for rank_list in user_profile_get
        ]
        return rank_list

    def get_user_profile_data(self, obj):
        user_profile_get = UserModel.objects.select_related("userprofile").get(
            id=obj.id
        )
        return {
            "grade": user_profile_get.userprofile.mongle_grade,
            "profile_img": user_profile_get.userprofile.profile_img,
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

        return bool(
            LetterreviewLikeModel.objects.filter(user=cur_user, letter_review=obj)
        )

    def get_review_id(self, obj):
        return obj.id

    def get_like_count(self, obj):
        return LetterreviewLikeModel.objects.filter(letter_review=obj).count()

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
        return bool(
            LetterreviewLikeModel.objects.filter(user=cur_user, letter_review=obj)
        )

    def get_review_id(self, obj):
        return obj.id

    def get_like_count(self, obj):
        return LetterreviewLikeModel.objects.filter(letter_review=obj).count()

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
