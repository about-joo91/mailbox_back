from rest_framework import serializers

from worry_board.models import WorryBoard as WorryBoardModel, RequestMessage as RequestMessageModel


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
        fields = ["id", "author", "category", "create_date", "content", "is_worry_board_writer"]

        extra_kwargs = {
            "author": {"write_only": True},
        }


class RequestMessageSerializer(serializers.ModelSerializer):
    create_date = serializers.SerializerMethodField()

    def get_create_date(self, obj):
        format_data = "%m-%d %H:%M"

        time = obj.create_date
        time_data = time.strftime(format_data)

        return time_data

    class Meta:
        model = RequestMessageModel
        fields = ["id", "author", "request_message", "worry_board", "create_date"]