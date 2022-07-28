from rest_framework import serializers

from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.models import WorryBoard as WorryBoardModel


class WorryBoardSerializer(serializers.ModelSerializer):
    create_date = serializers.SerializerMethodField()
    is_worry_board_writer = serializers.SerializerMethodField()

    def get_create_date(self, obj):
        format_data = "%m-%d %H:%M"
        time = obj.create_date
        time_data = time.strftime(format_data)

        return time_data

    def get_is_worry_board_writer(self, obj):
        cur_user = self.context["request"].user
        return bool(obj.author == cur_user)

    class Meta:
        model = WorryBoardModel
        fields = [
            "id",
            "author",
            "category",
            "create_date",
            "content",
            "is_worry_board_writer",
        ]

        extra_kwargs = {
            "author": {"write_only": True},
        }


class RequestMessageSerializer(serializers.ModelSerializer):
    create_date = serializers.SerializerMethodField()
    worry_board_category = serializers.SerializerMethodField()
    worry_board_content = serializers.SerializerMethodField()

    def get_create_date(self, obj):
        format_data = "%m-%d %H:%M"

        time = obj.create_date
        time_data = time.strftime(format_data)

        return time_data

    def get_worry_board_category(self, obj):
        return obj.worry_board.category.cate_name

    def get_worry_board_content(self, obj):
        return obj.worry_board.content

    class Meta:
        model = RequestMessageModel
        fields = [
            "id",
            "author",
            "request_message",
            "worry_board",
            "create_date",
            "worry_board_category",
            "worry_board_content",
        ]
