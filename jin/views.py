from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Category as CategoryModel
from .models import Letter as LetterModel
# Create your views here.
class MainPageView(APIView):
    """
    마이 페이지의 CRUD를 담당하는 View
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self, request):
        user = request.user.id
        letter_get = LetterModel.objects.all()
        
        
        print(letter_get)
        return Response({"get"}, status=status.HTTP_200_OK)