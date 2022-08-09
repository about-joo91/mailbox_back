from rest_framework import serializers

from board.models import Board as BoardModel
from board.models import BoardComment as BoardCommentModel
from user.models import UserProfile as UserProfileModel
from user.serializers import MongleGradeSerializer


class BoardSerializer(serializers.ModelSerializer):

    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_board_writer = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    board_comment = serializers.SerializerMethodField()
    board_comment_count = serializers.SerializerMethodField()
    create_date = serializers.SerializerMethodField()

    def get_like_count(self, obj):
        return obj.boardlike_set.count()

    def get_is_liked(self, obj):
        author = self.context["author"]
        return obj.boardlike_set.filter(author=author).exists()

    def get_is_board_writer(self, obj):
        cur_user = self.context["author"]
        return bool(obj.author == cur_user)

    def get_user_id(self, obj):
        return obj.author.id

    def get_board_comment(self, obj):
        author = self.context["author"]
        return BoardCommentSerializer(obj.boardcomment_set, many=True, context={"author": author}).data

    def get_board_comment_count(self, obj):
        return obj.boardcomment_set.count()

    def get_create_date(self, obj):
        format_data = "%m-%d %H:%M"

        time = obj.create_date
        time_data = time.strftime(format_data)

        return time_data

    class Meta:
        model = BoardModel
        fields = [
            "id",
            "title",
            "create_date",
            "content",
            "like_count",
            "is_liked",
            "is_board_writer",
            "user_id",
            "board_comment",
            "board_comment_count",
        ]


class BoardCommentSerializer(serializers.ModelSerializer):
    is_comment_writer = serializers.SerializerMethodField()
    is_detail_page_writer = serializers.SerializerMethodField()
    create_date = serializers.SerializerMethodField()

    def get_is_comment_writer(self, obj):
        author = self.context["author"]
        return bool(obj.author == author)

    def get_is_detail_page_writer(self, obj):
        is_detail = obj.author == obj.board.author
        if is_detail:
            return 1
        return 0

    def get_create_date(self, obj):
        format_data = "%m-%d %H:%M"

        time = obj.create_date
        time_data = time.strftime(format_data)

        return time_data

    class Meta:
        model = BoardCommentModel
        fields = [
            "id",
            "board",
            "create_date",
            "content",
            "is_comment_writer",
            "is_detail_page_writer",
        ]
        extra_kwargs = {"board": {"read_only": True}}


class UserProfileSerializer(serializers.ModelSerializer):
    mongle_grade = serializers.SerializerMethodField(read_only=True)

    def get_mongle_grade(self, obj):
        return MongleGradeSerializer(obj.user.monglegrade).data

    class Meta:
        model = UserProfileModel
        fields = [
            "mongle_grade",
            "profile_img",
        ]
