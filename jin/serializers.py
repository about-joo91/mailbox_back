from rest_framework import serializers
from .models import LetterReview as LetterReviewModel
from .models import Letter as LetterModel
from user.models import UserProfile as UserProfileModel
from worry_board.models import WorryBoard as WorryBoardModel


class MaiapageSerializer(serializers.ModelSerializer):
    best_review = serializers.SerializerMethodField()
    live_review = serializers.SerializerMethodField()
    worry_list = serializers.SerializerMethodField()
    rank_list = serializers.SerializerMethodField()

    def get_best_review(self, request):
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

    def get_live_review(self, request):
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

    def get_worry_list(self, request):
        worry_list = []
        for cate_get in range(1, 7):
            worry_gets = WorryBoardModel.objects.filter(category=cate_get).order_by(
                "-create_date"
            )[:3]
            for worry_get in worry_gets:
                cate = {
                    "worry_id": worry_get.id,
                    "category": worry_get.category.id,
                    "content": worry_get.content,
                }
                worry_list.append(cate)
        return worry_list

    def get_rank_list(self, requset):

        rank_list_get = UserProfileModel.objects.all().order_by("-mongle_grade")[:10]
        rank_list = [{"user": rank_list.user.username} for rank_list in rank_list_get]
        return rank_list

    class Meta:
        model = LetterReviewModel
        fields = ["rank_list", "worry_list", "best_review", "live_review"]


class LetterSerializer(serializers.ModelSerializer):
    letter_count = serializers.SerializerMethodField()

    def get_letter_count(self, request):
        count = request.userlettertargetuser_set.all().count()
        return count

    class Meta:
        model = LetterModel
        fields = ["letter_count"]
