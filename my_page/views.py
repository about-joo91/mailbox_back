from rest_framework import status
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

    authentication_classes = [JWTAuthentication]

    def get(self, request):
        cur_user = request.user
        my_letters = LetterModel.objects.filter(letter_author=cur_user)
        return Response(
            LetterSerializer(my_letters, many=True).data, status=status.HTTP_200_OK
        )


class MyRecievedLetterView(APIView):
    """
    내가 받은 편지를 조회하는 View
    """

    authentication_classes = [JWTAuthentication]

    def get(self, request):
        cur_user = request.user
        my_recieved_letter = LetterModel.objects.filter(
            userlettertargetuser__target_user=cur_user
        )
        return Response(
            LetterSerializer(my_recieved_letter, many=True).data,
            status=status.HTTP_200_OK,
        )
