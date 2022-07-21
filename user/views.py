from django.db.models import Q
from django.forms import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.services.user_profile_category_service import (
    create_category_of_profile,
    get_category_of_profile,
)
from user.services.user_profile_service import (
    get_user_profile_data,
    update_user_profile_data,
)

from .models import User as UserModel
from .models import UserProfile as UserProfileModel
from .models import UserProfileCategory as UserProfileCategoryModel
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
            profile_data = get_user_profile_data(cur_user)
            return Response(profile_data, status=status.HTTP_200_OK)
        except UserProfileModel.DoesNotExist:
            return Response(
                {"detail": "프로필이 없습니다. 프로필을 생성해주세요"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        cur_user = request.user
        update_data = request.data

        try:
            update_user_profile_data(user=cur_user, update_data=update_data)
            return Response({"detail": "프로필이 수정되었습니다"}, status=status.HTTP_200_OK)
        except ValidationError:
            return Response(
                {"detail": "프로필 수정에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileCategoryView(APIView):
    """
    유저 프로필에 카테고리를 조회 등록하고 지우는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        cur_user = request.user
        categories = get_category_of_profile(cur_user)
        return Response(categories, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        cur_user = request.user
        categories = request.data["categories"]
        try:
            create_category_of_profile(user=cur_user, categories=categories)
            return Response({"detail": "카테고리가 저장되었습니다."}, status=status.HTTP_200_OK)
        except UserProfileModel.DoesNotExist:
            return Response({"detail": "유저 프로필 정보가 없습니다."}, status=status.HTTP_404_OK)
        except UserModel.DoesNotExist:
            return Response({"detail": "유저가 없습니다."}, status=status.HTTP_404_OK)

    def delete(self, request: Request, p_category: str) -> Response:
        cur_user = request.user
        cur_user_profile = cur_user.userprofile
        user_cate = UserProfileCategoryModel.objects.get(
            Q(id=p_category) & Q(user_profile__id=cur_user_profile.id)
        )
        user_cate.delete()
        return Response({"message": "카테고리를 지웠습니다."}, status=status.HTTP_200_OK)
