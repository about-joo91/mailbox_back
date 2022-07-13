from rest_framework import serializers

from board.models import Board as BoardModel, BoardComment as BoardCommentModel


class BoardSerializer(serializers.ModelSerializer):
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_board_writer = serializers.SerializerMethodField()
    board_comment = serializers.SerializerMethodField()

    def get_like_count(self,obj):
        return obj.boardlike_set.count()

    def get_is_liked(self,obj):
        return bool(obj.boardlike_set.filter(board = obj.id))

    def get_is_board_writer(self,obj):
        cur_user = self.context['request'].user
        return bool(obj.author == cur_user)

    def get_board_comment(self, obj):
        request = self.context['request']
        return BoardCommentSerializer(obj.boardcomment_set, many=True, context={"request" : request}).data

    class Meta:
        model = BoardModel
        fields = ["id", "author", "title", "create_date", "content", "like_count", "is_liked", "is_board_writer", "board_comment"]

class BoardCommentSerializer(serializers.ModelSerializer):
    is_comment_writer = serializers.SerializerMethodField()

    def get_is_comment_writer(self,obj):
        print(self)
        cur_user = self.context['request'].user
        return bool(obj.author == cur_user)

    class Meta:
        model = BoardCommentModel
        fields = ["id", "author", "board", "create_date", "content", 'is_comment_writer']