from rest_framework import serializers

from main_page.models import Letter as LetterModel
from user.models import MongleGrade as MongleGradeModel
from user.models import User as UserModel


class MongleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MongleGradeModel
        fields = ["grade", "level", "mongle"]


class LetterUserSerializer(serializers.ModelSerializer):
    monglegrade = serializers.SerializerMethodField()
    profile_img = serializers.SerializerMethodField()

    def get_profile_img(self, obj):
        return obj.userprofile.profile_img

    def get_monglegrade(self, obj):
        return MongleSerializer(obj.monglegrade).data

    class Meta:
        model = UserModel
        fields = ["nickname", "profile_img", "monglegrade"]


class LetterSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    letter_author = serializers.SerializerMethodField(read_only=True)
    received_user = serializers.SerializerMethodField(read_only=True)

    def get_letter_author(self, obj):
        return LetterUserSerializer(obj.letter_author).data

    def get_received_user(self, obj):
        return LetterUserSerializer(obj.worryboard.author).data

    def get_category(self, obj):
        return obj.worryboard.category.cate_name

    class Meta:
        model = LetterModel
        fields = [
            "category",
            "title",
            "content",
            "create_date",
            "is_read",
            "letter_author",
            "received_user",
        ]
