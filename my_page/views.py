from django.db.models import Q
from rest_framework import exceptions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview
from main_page.services.letter_service import letter_is_read_service
from my_page.serializers import LetterUserSerializer
from my_page.services.letter_review_service import create_letter_review, delete_letter_review, edit_letter_review
from my_page.services.my_page_service import get_letter_data_by_user, get_not_read_letter_count
from user.models import User as UserModel

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
            cur_user.refresh_from_db()
            letter_cnt = cur_user.sent_letter_cnt
            letter_num = int(self.request.query_params.get("letter_num"))
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
                status=status.HTTP_404_NOT_FOUND,
            )
        except UserModel.userprofile.RelatedObjectDoesNotExist:
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except UserModel.monglegrade.RelatedObjectDoesNotExist:
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({"detail": "올바른 편지 번호를 입력해주세요."}, status=status.HTTP_404_NOT_FOUND)


class MyReceivedLetterView(APIView):
    """
    내가 받은 편지를 조회하는 View
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request: Request) -> Response:

        try:
            cur_user = request.user
            cur_user.refresh_from_db()
            letter_num = int(self.request.query_params.get("letter_num"))

            letter_cnt = cur_user.received_letter_cnt
            if not letter_cnt:
                return Response(
                    {"detail": "편지가 없습니다. 편지를 받으러 가볼까요?"},
                    status=status.HTTP_303_SEE_OTHER,
                )

            not_read_letter_query = Q(worryboard__author=cur_user) & Q(is_read=False)
            not_read_letter_cnt = get_not_read_letter_count(not_read_letter_query)

            letter_this_page_query = Q(worryboard__author=cur_user) & Q(is_read=True)
            letter_this_page = get_letter_data_by_user(query=letter_this_page_query, letter_num=letter_num)

            return Response(
                {
                    "letter": letter_this_page,
                    "letter_cnt": letter_cnt - not_read_letter_cnt,
                    "not_read_letter_cnt": not_read_letter_cnt,
                },
                status=status.HTTP_200_OK,
            )
        except LetterModel.DoesNotExist:
            return Response(LetterUserSerializer(cur_user).data, status=status.HTTP_202_ACCEPTED)
        except IndexError:
            return Response(
                {"detail": f"{letter_num}번째 편지를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except UserModel.userprofile.RelatedObjectDoesNotExist:
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except UserModel.monglegrade.RelatedObjectDoesNotExist:
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({"detail": "올바른 편지 번호를 입력해주세요."}, status=status.HTTP_404_NOT_FOUND)


class MyNotReadLetterView(APIView):
    """
    읽지않은 편지를 조회하는 view
    """

    def get(self, request: Request) -> Response:
        try:
            cur_user = request.user
            letter_num = int(self.request.query_params.get("letter_num"))

            query = Q(worryboard__author=cur_user) & Q(is_read=False)
            not_read_letter_cnt = get_not_read_letter_count(query)
            if not_read_letter_cnt == 0:
                return Response(
                    {},
                    status=status.HTTP_303_SEE_OTHER,
                )

            letter_this_page = get_letter_data_by_user(query=query, letter_num=letter_num)
            letter_is_read_service(user_id=cur_user.id, letter_id=int(letter_this_page["id"]))

            return Response(
                {
                    "letter": letter_this_page,
                    "letter_cnt": not_read_letter_cnt,
                    "not_read_letter_cnt": not_read_letter_cnt,
                },
                status=status.HTTP_200_OK,
            )
        except IndexError:
            return Response({"detail": f"{letter_num}번째 편지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except UserModel.userprofile.RelatedObjectDoesNotExist:
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except UserModel.monglegrade.RelatedObjectDoesNotExist:
            return Response({"detail": "잘못된 요청입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({"detail": "올바른 편지 번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)


class LetterReviewView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            letter_id = int(self.request.query_params.get("letter_id"))
            cur_user = request.user
            review_data = request.data
            create_letter_review(user=cur_user, letter_id=letter_id, review_data=review_data)
            return Response({"detail": "리뷰가 생성되었습니다."}, status=status.HTTP_201_CREATED)
        except exceptions.ValidationError:
            return Response({"detail": "리뷰 생성에 실패했습니다. 리뷰를 다시 한번 확인하신 후에 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({"detail": "편지를 찾을 수가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except LetterModel.DoesNotExist:
            return Response({"detail": "편지를 찾을 수가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionError:
            return Response({"detail": "생성 권한이 없습니다."}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

    def put(self, request: Request) -> Response:
        try:
            letter_review_id = int(self.request.query_params.get("letter_review_id"))
            cur_user = request.user
            edit_data = request.data
            print(edit_data)
            edit_letter_review(user=cur_user, letter_review_id=letter_review_id, edit_data=edit_data)
            return Response({"detail": "리뷰 수정이 완료되었습니다."}, status=status.HTTP_200_OK)
        except PermissionError:
            return Response({"detail": "수정권한이 없습니다."}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except exceptions.ValidationError:
            return Response({"detail": "리뷰 수정에 실패했습니다. 리뷰를 다시 한 번 확인하신 후에 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except LetterReview.DoesNotExist:
            return Response({"detail": "없는 리뷰에 접근하려고 합니다."}, status=status.HTTP_404_NOT_FOUND)
        except TypeError:
            return Response({"detail": "없는 리뷰에 접근하려고 합니다."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request: Request) -> Response:
        try:
            letter_review_id = int(self.request.query_params.get("letter_review_id"))
            cur_user = request.user
            delete_letter_review(user=cur_user, letter_review_id=letter_review_id)
            return Response({"detail": "리뷰 삭제가 완료되었습니다."}, status=status.HTTP_200_OK)
        except PermissionError:
            return Response({"detail": "삭제 권한이 없습니다."}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except LetterReview.DoesNotExist:
            return Response({"detail": "없는 리뷰에 접근하려고 합니다."}, status=status.HTTP_404_NOT_FOUND)
        except TypeError:
            return Response({"detail": "없는 리뷰에 접근하려고 합니다."}, status=status.HTTP_404_NOT_FOUND)
