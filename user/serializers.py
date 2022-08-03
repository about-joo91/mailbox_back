from rest_framework import serializers

from .models import MongleGrade
from .models import User as UserModel
from .models import UserProfile as UserProfileModel


class UserSignupSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if UserModel.objects.filter(nickname=data["nickname"]).exists():
            raise serializers.ValidationError("중복된 닉네임이 존재합니다.")

        condition = all(x not in ["!", "@", "#", "$", "%", "^", "&", "*", "_"] for x in data["password"])
        if len(data["username"]) < 4:
            raise serializers.ValidationError("아이디는 4자 이상 입력해주세요.")
        elif len(data["password"]) < 8 or condition:
            raise serializers.ValidationError("비밀번호는 8자 이상 특수문자 포함해 입력해주세요")
        return data

    def create(self, *args, **kwargs):
        user = super().create(*args, **kwargs)
        p = user.password
        user.set_password(p)
        user.save()
        UserProfileModel(user=user).save()
        MongleGrade(user=user).save()
        return user

    def update(ser, *args, **kwargs):
        user = super().create(*args, **kwargs)
        p = user.password
        user.set_password(p)
        user.save()
        return user

    class Meta:
        model = UserModel
        fields = "__all__"

        # 각 필드에 해당하는 다양한 옵션 지정
        extra_kwargs = {
            "username": {
                "error_messages": {
                    "required": "아이디를 입력해주세요.",
                },
                "required": True,
                "allow_null": False,
            },
            "nickname": {
                "error_messages": {"required": "닉네임을 입력해주세요."},
            },
        }


class MongleGradeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["mongle", "level", "grade"]
        model = MongleGrade


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    mongle_grade = serializers.SerializerMethodField(read_only=True)

    def get_categories(self, obj):
        return [{"id": cate.id, "cate_name": cate.category.cate_name} for cate in obj.userprofilecategory_set.all()]

    def get_mongle_grade(self, obj):
        return MongleGradeSerializer(obj.user.monglegrade).data

    def get_user(self, obj):
        return obj.user.nickname

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    class Meta:
        model = UserProfileModel
        fields = [
            "user",
            "description",
            "mongle_grade",
            "fullname",
            "profile_img",
            "categories",
        ]
