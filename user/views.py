from django.db import IntegrityError
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from jin.models import WorryCategory
from user.services.report_service import create_user_report
from user.services.user_profile_category_service import (
    create_category_of_profile,
    delete_category_of_profile,
    get_category_of_profile_except_mine,
)
from user.services.user_profile_service import (
    get_user_profile_data,
    update_user_profile_data,
)

from .models import User as UserModel
from .models import UserProfile as UserProfileModel
from .serializers import UserSignupSerializer


# Create your views here.
class UserView(APIView):
    """
    회원정보 조회 및 추가, 수정 및 탈퇴
    """

    def get(self, request):
        return Response(
            UserSignupSerializer(request.user).data, status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "회원가입 성공하였습니다"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return Response({"message": "수정이 완료되었습니다!"}, status=status.HTTP_200_OK)

    def delete(self, request):
        return Response({"message": "탈퇴가 완료되었습니다!"}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    유저 프로필을 가져오고 수정하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        cur_user = request.user
        try:
            profile_data = get_user_profile_data(cur_user.id)
            return Response(profile_data, status=status.HTTP_200_OK)
        except UserProfileModel.DoesNotExist:
            return Response(
                {"detail": "프로필이 없습니다. 프로필을 생성해주세요"}, status=status.HTTP_404_NOT_FOUND
            )

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
            return Response(
                {"detail": "프로필이 없습니다. 프로필을 생성해주세요"}, status=status.HTTP_404_NOT_FOUND
            )


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
            return Response(
                {"detail": "유저프로필 데이터가 없습니다. 생성해주세요"}, status=status.HTTP_404_NOT_FOUND
            )

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
            return Response(
                {"detail": "유저 프로필 정보가 없습니다. 생성해주세요"}, status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request: Request, p_category: str = None) -> Response:
        try:
            cur_user = request.user
            delete_category_of_profile(user_id=cur_user.id, p_category=p_category)
            return Response({"detail": "카테고리를 지웠습니다."}, status=status.HTTP_200_OK)
        except WorryCategory.DoesNotExist:
            return Response(
                {"detail": "카테고리를 조회할 수 없습니다. 다시 시도해주세요."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except UserProfileModel.DoesNotExist:
            return Response(
                {"detail": "유저 프로필 정보가 없습니다. 생성해주세요"}, status=status.HTTP_404_NOT_FOUND
            )


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
            return Response(
                {"detail": "이미 신고하셨습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        except UserModel.DoesNotExist:
            return Response(
                {"detail": f"{target_user_id}는 없는 유저입니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
