from rest_framework import serializers

from main_page.models import Letter as LetterModel


class LetterSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return obj.worryboard.category.cate_name

    class Meta:
        model = LetterModel
        fields = ["category", "title", "content", "create_date"]
