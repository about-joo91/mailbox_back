from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Woory_Category as Woory_CategoryModel
from .models import Letter as LetterModel
from .serializers import MainpageSerializer
# Create your views here.
class MainPageView(APIView):
    """
    마이 페이지의 CRUD를 담당하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        category_list =[]
        for cate_get in range(1,7):
            letter_gets = LetterModel.objects.filter(category=cate_get)[:3]
            for letter_get in letter_gets:
                cate = {
                "category": letter_get.category,
                "title": letter_get.title,
                "content": letter_get.content
                }
                category_list.append(cate)


        return Response({"cate_post":MainpageSerializer(category_list, many=True).data},status=status.HTTP_200_OK)


