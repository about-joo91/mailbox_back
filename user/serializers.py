from rest_framework import serializers

from .models import User as UserModel
from .models import UserProfile as UserProfileModel


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = "__all__"

    def create(self, *args, **kwargs):
        user = super().create(*args, **kwargs)
        p = user.password
        user.set_password(p)
        user.save()
        UserProfileModel(user=user).save()
        return user

    def update(ser, *args, **kwargs):
        user = super().create(*args, **kwargs)
        p = user.password
        user.set_password(p)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

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
            "mongle_level",
            "mongle_grade",
            "fullname",
            "profile_img",
        ]
