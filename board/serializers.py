from rest_framework import serializers

from board.models import Board as BoardModel
from board.models import BoardComment as BoardCommentModel


class BoardSerializer(serializers.ModelSerializer):
    
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_board_writer = serializers.SerializerMethodField()
    board_comment = serializers.SerializerMethodField()
    board_comment_count = serializers.SerializerMethodField()
    create_date = serializers.SerializerMethodField()

    def get_like_count(self, obj):
        return obj.boardlike_set.count()

    def get_is_liked(self, obj):
        cur_user = self.context["request"].user
        return bool(obj.boardlike_set.filter(author=cur_user.id))

    def get_is_board_writer(self, obj):
        cur_user = self.context["request"].user
        return bool(obj.author == cur_user)

    def get_board_comment(self, obj):
        request = self.context["request"]
        return BoardCommentSerializer(
            obj.boardcomment_set, many=True, context={"request": request}
        ).data

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
            "author",
            "title",
            "create_date",
            "content",
            "like_count",
            "is_liked",
            "is_board_writer",
            "board_comment",
            "board_comment_count",
        ]
        extra_kwargs = {"author": {"write_only": True}}


class BoardCommentSerializer(serializers.ModelSerializer):
    is_comment_writer = serializers.SerializerMethodField()
    is_detail_page_writer = serializers.SerializerMethodField()

    def get_is_comment_writer(self, obj):
        cur_user = self.context["request"].user
        return bool(obj.author == cur_user)

    def get_is_detail_page_writer(self, obj):
        is_detail = obj.author == obj.board.author
        if is_detail:
            return 1
        return 0

    class Meta:
        model = BoardCommentModel
        fields = [
            "id",
            "author",
            "board",
            "create_date",
            "content",
            "is_comment_writer",
            "is_detail_page_writer",
        ]
        extra_kwargs = {"author": {"write_only": True}}
