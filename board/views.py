from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from unsmile_filtering import pipe
from board.models import Board as BoardModel
from board.models import BoardComment as BoardCommentModel
from board.models import BoardLike as BoardLikeModel
from board.serializers import BoardCommentSerializer, BoardSerializer
from board.services import board_service

# Create your views here.


class BoardView(APIView):
    """
    board 게시판의 CRUD를 담당하는 view
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        page_num = int(self.request.query_params.get("page_num"))
        all_board_list, total_count = board_service.get_board_data(page_num)
        return Response(
            {
                "boards": BoardSerializer(
                    all_board_list, many=True, context={"request": request}
                ).data,
                "total_count": total_count,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        result = pipe(request.data["content"])[0]
        if result["label"] == "clean":
            board_service.create_board_data(request.data, request.user.id)
            return Response({"message": "게시글이 생성되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, board_id):
        result = pipe(request.data["content"])[0]
        if result["label"] == "clean":
            board_service.update_board_data(board_id, request.data)
            return Response({"message": "게시글이 수정되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, board_id):
        
        try:
            board_service.delete_board_data(board_id, request.user.id)
            return Response({"message": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except BoardModel.DoesNotExist:
            return Response({"message": "게시글이 존재x 되었습니다."}, status=status.HTTP_200_OK)
            # 에러 메시지를 보고 except 뒤에 붙일 것


class BorderLikeView(APIView):
    """
    Board 게시판의 좋아요를 post 하는 View
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, board_id):
        # 후에 like 됐을 때, 취소됐을 때 구분을 해주어야함
        board_service.make_or_delete_like_data(request.user, board_id)
        return Response({"message": "좋아요가 눌렸습니다!!"}, status=status.HTTP_200_OK)


class BorderCommentView(APIView):
    """
    Board 게시판의 댓글을 작성하고 불러오는 View
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        board_id = int(self.request.query_params.get("board_id")
        )
        return Response(
            {
                "board_comments": BoardSerializer(
                    board_service.get_board_comment_data(board_id), many=True, context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        board_id = int(self.request.query_params.get("board_id"))
        board_service.create_board_comment_data(request.user, board_id, request.data)
        return Response({"message": "댓글이 생성되었습니다."}, status=status.HTTP_200_OK)

    def put(self, request, comment_id):
        board_service.update_board_comment_data(request.data, comment_id)
        return Response({"message": "댓글이 수정되었습니다."}, status=status.HTTP_200_OK)

    def delete(self, request, comment_id):

        try:
            board_service.delete_board_comment_data(comment_id, request.user.id)
            return Response({"message": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except BoardCommentModel.DoesNotExist:
            return Response({"message": "댓글이 존재하지 않습니다.."}, status=status.HTTP_400_BAD_REQUEST)