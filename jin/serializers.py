from rest_framework import serializers

from user.models import UserProfile as UserProfileModel
from worry_board.models import WorryBoard as WorryBoardModel
from .models import (
    LetterReview as LetterReviewModel,
    Letter as LetterModel,
    UserLetterTargetUser as UserLetterTargetUserModel

)



class LetterSerilaizer(serializers.ModelSerializer):
    def create(self, validated_data):
        new_post = LetterModel.objects.create(
            **validated_data
        ) 
        new_post.save()
        target_user = validated_data.pop('worryboard')
        UserLetterTargetUserModel(letter= new_post, target_user = target_user.author).save()
        return new_post
        
    class Meta:
        model = LetterModel
        fields = ["letter_author","category","title","content","create_date","worryboard"]



class UserProfileSerializer(serializers.ModelSerializer):
    rank_list = serializers.SerializerMethodField()

    def get_rank_list(self,obj):    
        rank_list_get =UserProfileModel.objects.all().order_by("-mongle_grade")[:10]
        rank_list = [
            {
                "user": rank_list.user.username
            }
            for rank_list in rank_list_get
        ]
        return rank_list    
    class Meta:
        model = UserProfileModel
        fields = ["rank_list"]


class LetterReviewSerializer(serializers.ModelSerializer):
    best_review = serializers.SerializerMethodField()
    live_review = serializers.SerializerMethodField()

    def get_best_review(self,obj):
        best_review_get = LetterReviewModel.objects.all().order_by("-grade")[:3]
        best_review = [
            {
                "review_id": best_review.id,
                "content": best_review.content,
                "review_author": best_review.review_author.id,
                "grade": best_review.grade,
            }
            for best_review in best_review_get
        ]
        return best_review

    def get_live_review(self,request):
        live_review_get = LetterReviewModel.objects.all().order_by("-create_date")[:2]
        live_review = [
            {
                "review_id": live_review.id,
                "content": live_review.content,
                "review_author": live_review.review_author.id,
                "grade": live_review.grade,
            }
            for live_review in live_review_get
        ]
        return live_review
    class Meta:
        model = LetterReviewModel
        fields = ["best_review","live_review"]




