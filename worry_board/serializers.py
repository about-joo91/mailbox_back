from rest_framework import serializers

from worry_board.models import WorryBoard as WorryBoardModel


class WorryBoardSerializer(serializers.ModelSerializer):
    create_date = serializers.SerializerMethodField()

    def get_create_date(self, obj):
        format_data = "%m-%d %H:%M"

        time = obj.create_date
        time_data = time.strftime(format_data)

        return time_data

    class Meta:
        model = WorryBoardModel
        fields = ["id", "author", "category", "create_date", "content"]

        extra_kwargs = {
            "author": {"write_only": True},
        }
