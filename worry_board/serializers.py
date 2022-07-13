from rest_framework import serializers

from worry_board.models import WorryBoard as WorryBoardModel


class WorryBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorryBoardModel
        fields = ["id", "author", "category", "create_date", "content"]

        extra_kwargs = {
            "author": {"write_only": True},
        }
