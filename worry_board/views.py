from rest_framework import exceptions, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from recommendation.services.recomendation_service import recommend_worryboard_list
from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import RequestMessageSerializer, WorryBoardSerializer
from worry_board.services.worry_board_request_message_service import (
    accept_request_message_data,
    create_request_message_data,
    delete_request_message_data,
    disaccept_request_message_data,
    get_paginated_request_message_data,
    update_request_message_data,
)
from worry_board.services.worry_board_service import (
    check_is_it_clean_text,
    create_worry_board_data,
    delete_worry_board_data,
    get_paginated_worry_board_data,
    update_worry_board_data,
)


# Create your views here.
class WorryBoardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            category = int(self.request.query_params.get("category"))
            page_num = int(self.request.query_params.get("page_num"))
            if page_num == 0:
                page_num = 1

            try:
                recommended_worryboard = recommend_worryboard_list(request.user)
            except KeyError:
                recommended_worryboard = []
            except AttributeError:
                recommended_worryboard = []

            paginated_worry_board, total_count = get_paginated_worry_board_data(
                page_num, category, recommended_worryboard
            )

            return Response(
                {
                    "boards": WorryBoardSerializer(paginated_worry_board, many=True, context={"request": request}).data,
                    "total_count": total_count,
                    "recommended_cnt": len(recommended_worryboard),
                },
                status=status.HTTP_200_OK,
            )
        except TypeError:
            return Response({"detail": "게시판을 조회할 수 없습니다. 다시 시도해주세요."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        author = request.user
        if check_is_it_clean_text(request.data["content"]):
            try:
                create_worry_board_data(author, request.data)
                return Response({"detail": "고민 게시글을 게시하였습니다."}, status=status.HTTP_200_OK)
            except exceptions.ValidationError as e:
                error_message = "".join([str(value) for values in e.detail.values() for value in values])
                return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)
            except AssertionError:
                return Response(
                    {"detail": "category가 비어있습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, worry_board_id=0):
        author = request.user

        if worry_board_id == 0:
            return Response(
                {"detail": "worry_board_id가 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if WorryBoardModel.objects.get(id=worry_board_id).author != author:
            return Response(
                {"detail": "자기가 작성하지 않은 게시물은 수정이 불가합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if check_is_it_clean_text(request.data["content"]):
            try:
                update_worry_board_data(worry_board_id, request.data)
                return Response({"detail": "고민 게시글이 수정되었습니다."}, status=status.HTTP_200_OK)

            except TypeError:
                return Response(
                    {"detail": "parameter가 비어있습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except WorryBoardModel.DoesNotExist:
                return Response(
                    {"detail": "고민글이 존재하지 않습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except exceptions.ValidationError as e:
                error_message = "".join([str(value) for values in e.detail.values() for value in values])
                return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 게시글을 수정 할 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, worry_board_id=0):
        author = request.user
        if worry_board_id == 0:
            return Response(
                {"detail": "worry_board_id가 비어있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            delete_worry_board_data(author, worry_board_id)
            return Response({"detail": "고민 게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except WorryBoardModel.DoesNotExist:
            return Response(
                {"detail": "유저의 고민 게시글과 일치하는 게시글이 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )


class RequestMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    """
    보내거나 받은 request_message를 조회하는 view
    """

    def get(self, request, case):

        try:
            page_num = int(self.request.query_params.get("page_num"))
        except TypeError:
            page_num = 1
            author = request.user
            paginated_request_message, total_count = get_paginated_request_message_data(page_num, case, author)

            return Response(
                {
                    "request_message": RequestMessageSerializer(
                        paginated_request_message, many=True, context={"request": request}
                    ).data,
                    "total_count": total_count,
                },
                status=status.HTTP_200_OK,
            )

    def post(self, request, worry_board_id=0):
        """
        request 요청을 보내는 view
        """
        if worry_board_id == 0:
            return Response({"detail": "worry_board가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        author = request.user
        check_content = request.data["request_message"]

        if check_is_it_clean_text(check_content):
            if RequestMessageModel.objects.filter(author=author, worry_board_id=worry_board_id).exists():
                return Response(
                    {"detail": "이미 보낸 요청입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if WorryBoardModel.objects.filter(id=worry_board_id, author=author).exists():
                return Response({"detail": "내가 작성한 게시물에는 요청할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                create_request_message_data(author, worry_board_id, request.data)
                return Response({"detail": "게시물 작성자에게 요청하였습니다!"}, status=status.HTTP_200_OK)
            except exceptions.ValidationError as e:
                error_message = "".join([str(value) for values in e.detail.values() for value in values])
                return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)
            except WorryBoardModel.DoesNotExist:
                return Response({"detail": "worry_board가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 요청을 보낼 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, request_message_id):

        check_content = request.data["request_message"]
        if check_is_it_clean_text(check_content):
            try:
                update_request_message_data(request.data, request_message_id)
                return Response({"detail": "요청 메세지가 수정되었습니다."}, status=status.HTTP_200_OK)
            except RequestMessageModel.DoesNotExist:
                return Response({"detail": "해당 요청 메세지가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
            except exceptions.ValidationError as e:
                error_message = "".join([str(value) for values in e.detail.values() for value in values])
                return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 요청을 보낼 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, request_message_id):
        try:
            delete_request_message_data(request_message_id)
            return Response({"detail": "요청 메세지가 삭제되었습니다."}, status=status.HTTP_200_OK)
        except RequestMessageModel.DoesNotExist:
            return Response({"detail": "해당 요청 메세지가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)


class AcceptRequestMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    """
    request_message를 수락하는 View
    """

    def put(self, request, request_message_id, case):
        if case == "accept":
            try:
                request_message = RequestMessageModel.objects.get(id=request_message_id)
                if request_message.worry_board.author != request.user:
                    return Response({"detail": "수락 권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                if request_message.request_status.status == "반려됨":
                    return Response({"detail": "이미 거절한 요청은 수락할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                if request_message.request_status.status == "수락됨":
                    return Response({"detail": "이미 수락한 요청은 수락할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                accept_request_message_data(request_message_id)
                return Response({"detail": "요청 메세지를 수락하였습니다."}, status=status.HTTP_200_OK)
            except RequestMessageModel.DoesNotExist:
                return Response({"detail": "해당 요청은 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        elif case == "disaccept":
            try:
                request_message = RequestMessageModel.objects.get(id=request_message_id)
                if request_message.worry_board.author != request.user:
                    return Response({"detail": "거절 권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                if request_message.request_status.status == "수락됨":
                    return Response({"detail": "이미 수락한 요청은 거절할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
                if request_message.request_status.status == "반려됨":
                    return Response({"detail": "이미 거절한 요청은 거절할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

                disaccept_request_message_data(request_message_id)
                return Response({"detail": "요청 메세지를 거절하였습니다."}, status=status.HTTP_200_OK)

            except RequestMessageModel.DoesNotExist:
                return Response({"detail": "해당 요청은 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
