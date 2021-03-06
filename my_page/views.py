from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from main_page.services.letter_service import letter_is_read_service
from my_page.services.my_page_service import get_letter_data_by_user, get_not_read_letter_count
from user.models import MongleGrade as MongleGradeModel
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel

# Create your views here.


class MyLetterView(APIView):
    """
    내가 보낸 편지를 조회하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        cur_user = request.user
        try:
            letter_num = int(self.request.query_params.get("letter_num"))
        except TypeError:
            return Response({"detail": "올바른 편지 번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cur_user.refresh_from_db()
            letter_cnt = cur_user.sent_letter_cnt
            if letter_cnt == 0:
                return Response({"detail": "편지가 없습니다. 작성하러 가볼까요?"}, status=status.HTTP_303_SEE_OTHER)
            query = Q(letter_author=cur_user)
            letter_this_page = get_letter_data_by_user(query=query, letter_num=letter_num)
            return Response(
                {
                    "letter": letter_this_page,
                    "letter_cnt": letter_cnt,
                },
                status=status.HTTP_200_OK,
            )
        except IndexError:
            return Response(
                {"detail": f"{letter_num}번째 편지를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UserModel.userprofile.RelatedObjectDoesNotExist:
            UserProfileModel.objects.create(user=cur_user)
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."})
        except UserModel.monglegrade.RelatedObjectDoesNotExist:
            MongleGradeModel.objects.create(user=cur_user)
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."})


class MyRecievedLetterView(APIView):
    """
    내가 받은 편지를 조회하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:
        cur_user = request.user
        try:
            letter_num = int(self.request.query_params.get("letter_num"))
        except TypeError:
            return Response({"detail": "올바른 편지 번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cur_user.refresh_from_db()
            letter_cnt = cur_user.received_letter_cnt
            if letter_cnt == 0:
                return Response(
                    {"detail": "편지가 없습니다. 편지를 받으러 가볼까요?"},
                    status=status.HTTP_303_SEE_OTHER,
                )

            letter_this_page_query = Q(worryboard__author=cur_user)
            letter_this_page = get_letter_data_by_user(query=letter_this_page_query, letter_num=letter_num)

            not_read_letter_query = Q(worryboard__author=cur_user) & Q(is_read=False)
            not_read_letter_cnt = get_not_read_letter_count(not_read_letter_query)

            return Response(
                {
                    "letter": letter_this_page,
                    "letter_cnt": letter_cnt,
                    "not_read_letter_cnt": not_read_letter_cnt,
                },
                status=status.HTTP_200_OK,
            )
        except IndexError:
            return Response(
                {"detail": f"{letter_num}번째 편지를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UserModel.userprofile.RelatedObjectDoesNotExist:
            UserProfileModel.objects.create(user=cur_user)
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."})
        except UserModel.monglegrade.RelatedObjectDoesNotExist:
            MongleGradeModel.objects.create(user=cur_user)
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."})


class NotReadLetterView(APIView):
    def get(self, request: Request) -> Response:
        try:
            cur_user = request.user
            letter_num = int(self.request.query_params.get("letter_num"))

            query = Q(worryboard__author=cur_user) & Q(is_read=False)
            not_read_letter_cnt = get_not_read_letter_count(query)
            if not_read_letter_cnt == 0:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                )

            letter_this_page = get_letter_data_by_user(query=query, letter_num=letter_num)
            letter_is_read_service(user_id=cur_user.id, letter_id=int(letter_this_page["id"]))

            return Response(
                {
                    "letter": letter_this_page,
                    "not_read_letter_cnt": not_read_letter_cnt,
                },
                status=status.HTTP_200_OK,
            )
        except IndexError:
            return Response({"detail": f"{letter_num}번째 편지를 찾을 수 없습니다."})
        except UserModel.userprofile.RelatedObjectDoesNotExist:
            UserProfileModel.objects.create(user=cur_user)
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."})
        except UserModel.monglegrade.RelatedObjectDoesNotExist:
            MongleGradeModel.objects.create(user=cur_user)
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."})
        except TypeError:
            return Response({"detail": "올바른 편지 번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
