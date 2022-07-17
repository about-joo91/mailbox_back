from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from jin.models import Letter as LetterModel

from .serializers import LetterSerializer

# Create your views here.


class MyLetterView(APIView):
    """
    내가 보낸 편지를 조회하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        cur_user = request.user
        letter_num = int(self.request.query_params.get("letter_num"))
        letter_cnt = LetterModel.objects.filter(letter_author=cur_user).count()
        letter_this_page = LetterModel.objects.filter(letter_author=cur_user)[
            letter_num
        ]
        try:
            letter_this_page = LetterModel.objects.filter(letter_author=cur_user)[
                letter_num
            ]
            return Response(
                {
                    "is_letter_exist": True,
                    "letter": LetterSerializer(letter_this_page).data,
                    "letter_cnt": letter_cnt,
                },
                status=status.HTTP_200_OK,
            )
        except IndexError:
            return Response({"is_letter_exist": False}, status=status.HTTP_200_OK)


class MyRecievedLetterView(APIView):
    """
    내가 받은 편지를 조회하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        cur_user = request.user
        letter_num = int(self.request.query_params.get("letter_num"))
        letter_cnt = LetterModel.objects.filter(
            userlettertargetuser__target_user=cur_user
        ).count()
        try:
            letter_this_page = LetterModel.objects.filter(
                userlettertargetuser__target_user=cur_user
            )[letter_num]
            return Response(
                {
                    "is_letter_exist": True,
                    "letter": LetterSerializer(letter_this_page).data,
                    "letter_cnt": letter_cnt,
                },
                status=status.HTTP_200_OK,
            )
        except IndexError:
            return Response({"is_letter_exist": False}, status=status.HTTP_200_OK)
