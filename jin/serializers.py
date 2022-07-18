from rest_framework import serializers

from user.models import UserProfile as UserProfileModel

from .models import Letter as LetterModel
from .models import LetterReview as LetterReviewModel
from .models import LetterReviewLike as LetterreviewLikeModel
from .models import UserLetterTargetUser as UserLetterTargetUserModel


class LetterSerilaizer(serializers.ModelSerializer):
    def create(self, validated_data):
        new_post = LetterModel.objects.create(**validated_data)
        new_post.save()
        target_user = validated_data.pop("worryboard")
        UserLetterTargetUserModel(
            letter=new_post, target_user=target_user.author
        ).save()
        return new_post

    class Meta:
        model = LetterModel
        fields = [
            "letter_author",
            "category",
            "title",
            "content",
            "create_date",
            "worryboard",
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    rank_list = serializers.SerializerMethodField()

    def get_rank_list(self, obj):
        rank_list_get = UserProfileModel.objects.all().order_by("-mongle_grade")[:10]
        rank_list = [
            {"user": rank_list.user.username, "profile_img": rank_list.profile_img}
            for rank_list in rank_list_get
        ]
        return rank_list

    class Meta:
        model = UserProfileModel
        fields = ["rank_list"]


class BestReviewSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    review_id = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    def get_is_liked(self, obj):
        cur_user = self.context["request"].user

        return bool(
            LetterreviewLikeModel.objects.filter(user_id=cur_user, review_id=obj)
        )

    def get_review_id(self, obj):
        return obj.id

    def get_like_count(self, obj):
        return LetterreviewLikeModel.objects.filter(review_id=obj).count()

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
            LetterreviewLikeModel.objects.filter(user_id=cur_user, review_id=obj)
        )

    def get_review_id(self, obj):
        return obj.id

    def get_like_count(self, obj):
        return LetterreviewLikeModel.objects.filter(review_id=obj).count()

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
