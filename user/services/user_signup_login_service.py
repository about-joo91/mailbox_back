from typing import Dict

from django.db import transaction

from user.models import User
from user.serializers import UserSignupSerializer


def get_user_signup_data(user: User) -> Dict:
    """
    유저 정보를 get
    """
    return UserSignupSerializer(user).data


@transaction.atomic
def post_user_signup_data(user_data: Dict) -> None:
    """
    회원가입
    """
    user_data_serializer = UserSignupSerializer(data=user_data)
    user_data_serializer.is_valid(raise_exception=True)
    user_data_serializer.save()


def check_author(certification_data: Dict[str, str]):
    """
    username을 기반으로 User모델에서 탐색
    """
    check_user = User.objects.get(username=certification_data["username"])
    return check_user


def check_certification_question(certification_data: Dict[str, str]):
    """
    유저의 본인확인 질문 매칭
    """
    author = User.objects.get(username=certification_data["username"])
    return author.certification_answer == certification_data["certification_answer"]


def update_user_new_password(user: User, update_data: Dict) -> None:
    """
    비밀번호 새로 설정
    """
    update_user_serializer = UserSignupSerializer(user, data=update_data, partial=True)
    update_user_serializer.is_valid(raise_exception=True)
    update_user_serializer.save()
