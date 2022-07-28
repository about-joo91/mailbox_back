from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from board.models import Board as BoardModel
from board.models import BoardComment as BoardCommentModel
from board.models import BoardLike as BoardLikeModel
from board.serializers import BoardCommentSerializer, BoardSerializer
from board.services.board_service import (
    check_is_it_clean_text,
    create_board_comment_data,
    create_board_data,
    delete_board_comment_data,
    delete_board_data,
    delete_like_data,
    get_board_comment_data,
    get_paginated_board_data,
    make_like_data,
    update_board_comment_data,
    update_board_data,
)

# Create your views here.


class BoardView(APIView):
    """
    board 게시판의 CRUD를 담당하는 view
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        page_num = int(self.request.query_params.get("page_num"))
        paginated_board, total_count = get_paginated_board_data(page_num)
        return Response(
            {
                "boards": BoardSerializer(
                    paginated_board, many=True, context={"request": request}
                ).data,
                "total_count": total_count,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if check_is_it_clean_text(request.data["content"]):
            create_board_data(request.data, request.user.id)
            return Response({"detail": "게시글이 생성되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, board_id):
        if check_is_it_clean_text(request.data["content"]):
            update_board_data(board_id, request.data)
            return Response({"detail": "게시글이 수정되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 게시글을 수정 할 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, board_id):
        try:
            delete_board_data(board_id, request.user.id)
            return Response({"detail": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except BoardModel.DoesNotExist:
            return Response(
                {"detail": "게시글이 존재하지 않습니다"}, status=status.HTTP_400_BAD_REQUEST
            )


class BorderLikeView(APIView):
    """
    Board 게시판의 좋아요를 post 하는 View
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, board_id):
        author = request.user
        try:
            delete_like_data(author, board_id)
            return Response({"detail": "좋아요가 삭제되었습니다!!"}, status=status.HTTP_200_OK)
        except:
            make_like_data(author, board_id)
            return Response({"detail": "좋아요가 되었습니다!!"}, status=status.HTTP_200_OK)


class BorderCommentView(APIView):
    """
    Board 게시판의 댓글을 작성하고 불러오는 View
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        board_id = int(self.request.query_params.get("board_id"))
        board_comment_data = get_board_comment_data(board_id)
        return Response(
            {
                "board_comments": BoardSerializer(
                    board_comment_data, many=True, context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        author = request.user
        board_id = int(self.request.query_params.get("board_id"))
        if check_is_it_clean_text(request.data["content"]):
            create_board_comment_data(author, board_id, request.data)
            return Response({"detail": "댓글이 생성되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 댓글을 작성 할 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, comment_id):
        if check_is_it_clean_text(request.data["content"]):
            update_board_comment_data(request.data, comment_id)
            return Response({"detail": "댓글이 수정되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 댓글을 수정 할 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, comment_id):

        try:
            delete_board_comment_data(comment_id, request.user.id)
            return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except BoardCommentModel.DoesNotExist:
            return Response(
                {"detail": "댓글이 존재하지 않습니다.."}, status=status.HTTP_400_BAD_REQUEST
            )
