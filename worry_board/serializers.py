DOESNOTEXIXT = -1
from rest_framework import serializers

from user.models import User
from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.models import WorryBoard as WorryBoardModel


class WorryBoardSerializer(serializers.ModelSerializer):
    create_date = serializers.SerializerMethodField()
    is_worry_board_writer = serializers.SerializerMethodField()
    request_status = serializers.SerializerMethodField()
    request_message_id = serializers.SerializerMethodField()
    user_profile_data = serializers.SerializerMethodField()

    def get_create_date(self, obj):
        format_data = "%m-%d %H:%M"
        time = obj.create_date
        time_data = time.strftime(format_data)

        return time_data

    def get_is_worry_board_writer(self, obj):
        author = self.context["request"].user
        return bool(obj.author == author)

    def get_request_status(self, obj):
        author = self.context["request"].user

        try:
            return obj.requestmessage_set.get(author=author).request_status.status
        except RequestMessageModel.DoesNotExist:
            return "요청"

    def get_request_message_id(self, obj):
        author = self.context["request"].user
        try:
            return obj.requestmessage_set.get(author=author).id
        except RequestMessageModel.DoesNotExist:
            return DOESNOTEXIXT

    def get_user_profile_data(self, obj):
        cur_user = self.context["request"].user
        return {
            "grade": User.objects.get(id=cur_user.id).monglegrade.grade,
            "profile_img": User.objects.get(id=cur_user.id).userprofile.profile_img,
            "mongle_img": User.objects.get(id=cur_user.id).monglegrade.mongle,
        }

    class Meta:
        model = WorryBoardModel
        fields = [
            "id",
            "category",
            "create_date",
            "content",
            "is_worry_board_writer",
            "user_profile_data",
            "request_status",
            "request_message_id",
        ]

        extra_kwargs = {"request_status": {"read_only": True}}


class RequestMessageSerializer(serializers.ModelSerializer):
    create_date = serializers.SerializerMethodField()
    worry_board_category = serializers.SerializerMethodField()
    worry_board_content = serializers.SerializerMethodField()
    user_profile_data = serializers.SerializerMethodField()

    def get_create_date(self, obj):
        format_data = "%m-%d %H:%M"

        time = obj.create_date
        time_data = time.strftime(format_data)

        return time_data

    def get_worry_board_category(self, obj):
        return obj.worry_board.category.cate_name

    def get_worry_board_content(self, obj):
        return obj.worry_board.content

    def get_user_profile_data(self, obj):
        cur_user = self.context["request"].user
        return {
            "grade": User.objects.get(id=cur_user.id).monglegrade.grade,
            "profile_img": User.objects.get(id=cur_user.id).userprofile.profile_img,
            "mongle_img": User.objects.get(id=cur_user.id).monglegrade.mongle,
        }

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
            "request_status",
            "can_write_letter",
            "user_profile_data",
        ]
        extra_kwargs = {
            "author": {"read_only": True},
            "worry_board": {"read_only": True},
            "request_status": {"read_only": True},
        }
