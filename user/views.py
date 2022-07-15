from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from jin.models import WorryCategory as WorryCategoryModel

from .models import UserProfileCategory as UserProfileCategoryModel
from .serializers import UserProfileSerializer, UserSignupSerializer


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

    def get(self, request):
        cur_user = request.user

        return Response(
            UserProfileSerializer(cur_user.userprofile).data, status=status.HTTP_200_OK
        )

    def put(self, request):
        cur_user = request.user

        user_profile_serializer = UserProfileSerializer(
            cur_user.userprofile, data=request.data, partial=True
        )
        user_profile_serializer.is_valid(raise_exception=True)
        user_profile_serializer.save()

        return Response({"message": "프로필 수정이 완료되었습니다."}, status=status.HTTP_200_OK)


class UserProfileCategoryView(APIView):
    """
    유저 프로필에 카테고리를 조회 등록하고 지우는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        cur_user = request.user
        my_categories = cur_user.userprofile.categories.all()
        category_all_except_mine = WorryCategoryModel.objects.all().exclude(
            id__in=my_categories
        )
        categories = [
            {"id": cate.id, "cate_name": cate.cate_name}
            for cate in category_all_except_mine
        ]
        return Response(categories, status=status.HTTP_200_OK)

    def post(self, request):
        cur_user = request.user
        categories = request.data["categories"]
        cur_user.userprofile.categories.add(*categories)
        return Response({"message": "카테고리가 저장되었습니다."}, status=status.HTTP_200_OK)

    def delete(self, request, p_category):
        cur_user = request.user
        cur_user_profile = cur_user.userprofile
        user_cate = UserProfileCategoryModel.objects.get(
            Q(id=p_category) & Q(user_profile__id=cur_user_profile.id)
        )
        user_cate.delete()
        return Response({"message": "카테고리를 지웠습니다."}, status=status.HTTP_200_OK)
