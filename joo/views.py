from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


class MyPageView(APIView):
    """
    마이 페이지의 CRUD를 담당하는 View
    """

    def get(self, request):
        return Response({"get"}, status=status.HTTP_200_OK)

    def post(self, request):
        return Response({"post"}, status=status.HTTP_200_OK)

    def put(self, request):
        return Response({"put"}, status=status.HTTP_200_OK)

    def delete(self, request):
        return Response({"delete"}, status=status.HTTP_200_OK)
