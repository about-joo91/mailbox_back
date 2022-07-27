from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication


import unsmile_filtering
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
        filtering_sys = unsmile_filtering.post_filtering
        result = filtering_sys.unsmile_filter(request.data["content"])
        if result["label"] == "clean":
            try :
                board_service.create_board_data(request.data, request.user.id)
                return Response({"detail": "게시글이 생성되었습니다."}, status=status.HTTP_200_OK)
            except  BoardModel.DoesNotExist:
                return Response({"detail": "게시글이 생성에 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, board_id):
        filtering_sys = unsmile_filtering.post_filtering
        result = filtering_sys.unsmile_filter(request.data["content"])
        if result["label"] == "clean":
            board_service.update_board_data(board_id, request.data)
            return Response({"detail": "게시글이 수정되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, board_id):
        
        try:
            board_service.delete_board_data(board_id, request.user.id)
            return Response({"detail": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except BoardModel.DoesNotExist:
            return Response({"detail": "게시글이 존재하지 않습니다"}, status=status.HTTP_400_BAD_REQUEST)


class BorderLikeView(APIView):
    """
    Board 게시판의 좋아요를 post 하는 View
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, board_id):
        try : 
            board_service.delete_like_data(request.user, board_id) 
            return Response({"detail": "좋아요가 삭제되었습니다!!"}, status=status.HTTP_200_OK)
        except:
            board_service.make_like_data(request.user, board_id) 
            return Response({"detail": "좋아요가 되었습니다!!"}, status=status.HTTP_200_OK)


class BorderCommentView(APIView):
    """
    Board 게시판의 댓글을 작성하고 불러오는 View
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        board_id = int(self.request.query_params.get("board_id"))
        board_comment_data = board_service.get_board_comment_data(board_id)
        return Response(
            {
                "board_comments": BoardSerializer(
                    board_comment_data, many=True, context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        filtering_sys = unsmile_filtering.post_filtering
        result = filtering_sys.unsmile_filter(request.data["content"])
        if result["label"] == "clean":
            board_id = int(self.request.query_params.get("board_id"))
            board_service.create_board_comment_data(request.user.id, board_id, request.data)
            return Response({"detail": "댓글이 생성되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, comment_id):
        update_comment = BoardCommentModel.objects.get(id=comment_id)
        filtering_sys = unsmile_filtering.post_filtering
        result = filtering_sys.unsmile_filter(request.data["content"])
        if result["label"] == "clean":
            board_service.update_board_comment_data(request.data, comment_id)
            return Response({"detail": "댓글이 수정되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, comment_id):

        try:
            board_service.delete_board_comment_data(comment_id, request.user.id)
            return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except BoardCommentModel.DoesNotExist:
            return Response({"detail": "댓글이 존재하지 않습니다.."}, status=status.HTTP_400_BAD_REQUEST)