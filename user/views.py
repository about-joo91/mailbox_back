from django.db import IntegrityError
from rest_framework import exceptions, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserCertificationSerializer
from user.services.report_service import create_user_report
from user.services.user_profile_category_service import (
    create_category_of_profile,
    delete_category_of_profile,
    get_category_of_profile_except_mine,
)
from user.services.user_profile_service import get_user_profile_data, update_user_profile_data
from user.services.user_signup_login_service import (
    check_certification_question,
    check_is_user,
    check_password_in_signup_data,
    get_certification_question_list,
    get_user_signup_data,
    post_user_signup_data,
    update_user_certification_question,
    update_user_new_password,
)

from .models import MongleGrade
from .models import User as UserModel
from .models import UserProfile as UserProfileModel
from .models import UserProfileCategory


# Create your views here.
class UserView(APIView):
    """
    회원정보 조회 및 회원가입
    """

    def get(self, request: Request) -> Response:
        user_data = get_user_signup_data(request.user)
        return Response(user_data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        if check_password_in_signup_data(request.data):
            try:
                post_user_signup_data(request.data)
                return Response({"detail": "회원가입을 성공하였습니다"}, status=status.HTTP_200_OK)
            except exceptions.ValidationError as e:
                error = "\n".join([str(value) for values in e.detail.values() for value in values])
                return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "비밀번호와 비밀번호 확인이 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request) -> Response:
        if check_password_in_signup_data(request.data):
            update_user_new_password(request.data)
            return Response({"detail": "비밀번호를 새로 설정하였습니다."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "비밀번호와 비밀번호 확인이 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)


class CheckUserView(APIView):
    """
    새로운 비밀번호 설정을 위한 계정 탐색
    """

    def post(self, request: Request) -> Response:
        try:
            check_is_user(request.data["username"])
            return Response({"detail": "일치하는 계정을 찾았습니다."}, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response({"detail": "일치하는 계정이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)


class SignUpCertificationQuestionView(APIView):
    """
    회원가입시 certification_question을 불러오는 View
    """

    def get(self, request: Request) -> Response:
        certification_question_list = get_certification_question_list()
        return Response(certification_question_list, status=status.HTTP_200_OK)


class UserCertificationView(APIView):
    """
    본인 확인 질문을 대조하는 View
    """

    def get(self, request) -> Response:
        try:
            username = self.request.query_params.get("username")
            author = check_is_user(username)
            user_certification_question = UserCertificationSerializer(author).data
            return Response({"certification_request": user_certification_question})
        except AttributeError:
            return Response({"detail": "회원가입시 입력하지 않아 비밀번호를 찾을 수 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request) -> Response:
        if check_certification_question(request.data):
            return Response({"detail": "본인인증에 성공하였습니다."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "답변이 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)


class UserCertificationupdateView(APIView):
    """
    user의 본인 확인 질문을 업데이트 하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request: Request) -> Response:
        update_user_certification_question(request.user.id, request.data)
        return Response({"detail": "본인확인 질문이 업데이트 되었습니다"}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    유저 프로필을 가져오고 수정하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        cur_user = request.user
        try:
            certification_question_list = get_certification_question_list()

            profile_data = get_user_profile_data(cur_user.id)
            return Response(
                {"profile_data": profile_data, "certification_question_list": certification_question_list},
                status=status.HTTP_200_OK,
            )
        except UserProfileModel.DoesNotExist:
            UserProfileModel.objects.create(user=cur_user)
            return Response({"detail": "잘못된 접근입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except MongleGrade.DoesNotExist:
            MongleGrade.objects.create(user=cur_user)
            return Response({"detail": "잘못된 접근입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request: Request) -> Response:
        try:
            cur_user = request.user
            update_data = request.data
            update_user_profile_data(user_id=cur_user.id, update_data=update_data)
            return Response({"detail": "프로필이 수정되었습니다"}, status=status.HTTP_200_OK)
        except serializers.ValidationError:
            return Response(
                {"detail": "프로필 수정에 실패했습니다. 정확한 값을 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UserProfileModel.DoesNotExist:
            UserProfileModel.objects.create(user=cur_user)
            return Response({"detail": "잘못된 접근입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except MongleGrade.DoesNotExist:
            MongleGrade.objects.create(user=cur_user)
            return Response({"detail": "잘못된 접근입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileCategoryView(APIView):
    """
    유저 프로필에 카테고리를 조회 등록하고 지우는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        try:
            cur_user = request.user
            categories = get_category_of_profile_except_mine(cur_user.id)
            return Response(categories, status=status.HTTP_200_OK)
        except UserProfileModel.DoesNotExist:
            return Response({"detail": "유저프로필 데이터가 없습니다. 생성해주세요"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request: Request) -> Response:
        try:
            cur_user = request.user
            categories = request.data["categories"]
            create_category_of_profile(user_id=cur_user.id, categories=categories)
            return Response({"detail": "카테고리가 저장되었습니다."}, status=status.HTTP_200_OK)
        except ValueError:
            return Response(
                {"detail": "카테고리 생성에 실패했습니다. 정확한 값을 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UserProfileModel.DoesNotExist:
            return Response({"detail": "유저 프로필 정보가 없습니다. 생성해주세요"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request: Request, p_category: str = None) -> Response:
        try:
            cur_user = request.user
            delete_category_of_profile(user_id=cur_user.id, p_category=p_category)
            return Response({"detail": "카테고리를 지웠습니다."}, status=status.HTTP_200_OK)
        except UserProfileCategory.DoesNotExist:
            return Response(
                {"detail": "해당 카테고리를 조회할 수 없습니다. 다시 시도해주세요."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except PermissionError:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)


class ReportUserView(APIView):
    """
    유저를 신고하는 기능을 담당하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request: Request) -> Response:
        try:
            cur_user = request.user
            target_user_id = request.data["target_user_id"]
            report_reason = request.data["report_reason"]
            target_username = create_user_report(
                user_id=cur_user.id,
                target_user_id=target_user_id,
                report_reason=report_reason,
            )
            return Response({"detail": f"{target_username}유저를 신고하셨습니다."})
        except IntegrityError:
            return Response({"detail": "이미 신고하셨습니다."}, status=status.HTTP_400_BAD_REQUEST)
        except UserModel.DoesNotExist:
            return Response(
                {"detail": f"{target_user_id}는 없는 유저입니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
