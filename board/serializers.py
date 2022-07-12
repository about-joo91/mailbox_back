from dataclasses import field
from rest_framework import serializers

from board.models import Board as BoardModel


class BoardSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BoardModel
        fields = ["id", "author", "title", "create_date", "content"]
