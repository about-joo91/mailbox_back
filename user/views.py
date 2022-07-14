from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

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
