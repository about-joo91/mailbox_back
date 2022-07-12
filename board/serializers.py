from dataclasses import field
from rest_framework import serializers

from board.models import Board as BoardModel, BoardComment as BoardCommentModel


class BoardSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BoardModel
        fields = ["id", "author", "title", "create_date", "content"]

class BoardCommentSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = BoardCommentModel
        fields = ["id", "author", "board", "create_date", "content"]