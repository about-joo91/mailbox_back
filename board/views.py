from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from board.models import Board as BoardModel
from board.models import BoardComment
from board.models import BoardLike as BoardLikeModel
from board.serializers import BoardCommentSerializer, BoardSerializer
from unsmile_filtering import pipe

# Create your views here.


class BoardView(APIView):
    """
    board 게시판의 CRUD를 담당하는 view
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, page_num):
        all_board_list = BoardModel.objects.all().order_by("-create_date")[
            10 * (page_num - 1) : 9 + 10 * (page_num - 1)
        ]
        total_count = BoardModel.objects.all().order_by("-create_date").count()
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
            request.data["author"] = request.user.id
            create_board_serializer = BoardSerializer(data=request.data)
            create_board_serializer.is_valid(raise_exception=True)
            create_board_serializer.save()
            return Response({"message": "게시글이 생성되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, board_id):
        result = pipe(request.data["content"])[0]
        if result["label"] == "clean":
            update_board = BoardModel.objects.get(id=board_id)
            update_board_serializer = BoardSerializer(
                update_board, data=request.data, partial=True
            )
            update_board_serializer.is_valid(raise_exception=True)
            update_board_serializer.save()
            return Response({"message": "게시글이 수정되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, board_id):
        delete_board = BoardModel.objects.get(id=board_id)
        if delete_board:
            delete_board.delete()
            return Response({"message": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        return Response({"message": "삭제에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)


class BorderLikeView(APIView):
    """
    Board 게시판의 좋아요를 post 하는 View
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, board_id):
        author = request.user
        target_board = BoardModel.objects.get(id=board_id)
        liked_board, created = BoardLikeModel.objects.get_or_create(
            author=author, board=target_board
        )
        if created:
            liked_board.save()
            return Response({"message": "좋아요가 완료 되었습니다!!"}, status=status.HTTP_200_OK)
        liked_board.delete()
        return Response({"message": "좋아요가 취소 되었습니다!!"}, status=status.HTTP_200_OK)


class BorderCommentView(APIView):
    """
    Board 게시판의 댓글을 작성하고 불러오는 View
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        all_board_list = BoardComment.objects.all().order_by("-create_date")
        return Response(
            {
                "boards": BoardCommentSerializer(
                    all_board_list, many=True, context={"request": request}
                ).data
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, obj_id):
        # obj_id는 board_id 입니다.
        request.data["author"] = request.user.id
        request.data["board"] = obj_id
        create_board_comment_serializer = BoardCommentSerializer(data=request.data)
        create_board_comment_serializer.is_valid(raise_exception=True)
        create_board_comment_serializer.save()
        return Response({"message": "댓글이 생성되었습니다."}, status=status.HTTP_200_OK)
