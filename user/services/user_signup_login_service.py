from typing import Dict

from user.models import User
from user.serializers import UserSignupSerializer


def get_user_signup_data(user: User) -> Dict:
    """
    유저 정보를 get
    """
    return UserSignupSerializer(user).data


def post_user_signup_data(user_data: Dict) -> None:
    """
    회원가입
    """
    user_data_serializer = UserSignupSerializer(data=user_data)
    user_data_serializer.is_valid(raise_exception=True)
    user_data_serializer.save()
    
