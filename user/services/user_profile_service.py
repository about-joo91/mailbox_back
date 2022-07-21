from typing import Dict

from user.models import User
from user.serializers import UserProfileSerializer


def get_user_profile_data(user: User) -> Dict:
    return UserProfileSerializer(user.userprofile).data


def update_user_profile_data(user: User, update_data: Dict) -> None:
    user_profile_serializer = UserProfileSerializer(
        user.userprofile, data=update_data, partial=True
    )
    if user_profile_serializer.is_valid():
        user_profile_serializer.save()
