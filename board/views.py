from django.db.models import Q
from rest_framework import exceptions, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from board.models import Board as BoardModel
from board.models import BoardComment as BoardCommentModel
from board.models import BoardLike as BoardLikeModel
from board.services.board_service import (
    check_is_it_clean_text,
    create_board_comment_data,
    create_board_data,
    delete_board_comment_data,
    delete_board_data,
    delete_like_data,
    get_board_comment_data,
    get_paginated_board_data,
    get_searched_data,
    get_user_profile_data,
    make_like_data,
    update_board_comment_data,
    update_board_data,
)
from user.models import MongleGrade
from user.models import UserProfile as UserProfileModel


# Create your views here.
class BoardView(APIView):
    """
    board 게시판의 CRUD를 담당하는 view
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            try:
                is_mine = bool(self.request.query_params.get("is_mine"))
            except ValueError:
                return Response({"detail": "입력데이터를 수정해주세요."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                page_num = int(self.request.query_params.get("page_num"))
            except ValueError:
                return Response({"detail": "입력데이터를 수정해주세요."}, status=status.HTTP_400_BAD_REQUEST)

            author = request.user

            if is_mine:
                board_query = Q(author=author)
            else:
                board_query = Q()

            paginated_boards, total_count = get_paginated_board_data(
                page_num=page_num, author=author, query=board_query
            )
            user_profile_data = get_user_profile_data(request.user)

            return Response(
                {
                    "boards": paginated_boards,
                    "total_count": total_count,
                    "user_profile_data": user_profile_data,
                },
                status=status.HTTP_200_OK,
            )
        except TypeError:
            return Response({"detail": "게시판을 조회할 수 없습니다. 다시 시도해주세요."}, status=status.HTTP_404_NOT_FOUND)
        except exceptions.ValidationError as e:
            error = "".join([str(value) for values in e.detail.values() for value in values])
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        try:
            if check_is_it_clean_text(request.data["content"]):
                create_board_data(request.data, request.user)
                return Response({"detail": "몽글점수를 5점 획득 하셨습니다!"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except exceptions.ValidationError as e:
            error_message = " ".join([str(value) for values in e.detail.values() for value in values])
            return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, board_id: str = None):
        try:
            if check_is_it_clean_text(request.data["content"]):
                update_board_data(board_id, request.data, request.user)
                return Response({"detail": "게시글이 수정되었습니다."}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "부적절한 내용이 담겨있어 게시글을 수정 할 수 없습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except BoardModel.DoesNotExist:
            return Response({"detail": "게시글이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)
        except exceptions.PermissionDenied:
            return Response({"detail": "게시글 수정 권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)
        except exceptions.ValidationError as e:
            error_message = "".join([str(value) for values in e.detail.values() for value in values])
            return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, board_id: str = None):
        try:
            delete_board_data(board_id, request.user)
            return Response({"detail": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except BoardModel.DoesNotExist:
            return Response({"detail": "게시글이 존재하지 않습니다"}, status=status.HTTP_404_NOT_FOUND)
        except exceptions.PermissionDenied:
            return Response({"detail": "게시글 삭제 권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)


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
        except BoardLikeModel.DoesNotExist:
            make_like_data(author, board_id)
            return Response({"detail": "좋아요가 되었습니다!!"}, status=status.HTTP_200_OK)


class BorderCommentView(APIView):
    """
    Board 게시판의 댓글을 작성하고 불러오는 View
    """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            author = request.user
            board_id = int(self.request.query_params.get("board_id"))
            board_comments = get_board_comment_data(board_id, author)
            user_profile_data = get_user_profile_data(author)
            return Response(
                {"board_comments": board_comments, "user_profile_data": user_profile_data},
                status=status.HTTP_200_OK,
            )
        except TypeError:
            return Response(
                {"detail": "params의 board_id가 비어있습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        author = request.user
        board_id = int(self.request.query_params.get("board_id"))
        if check_is_it_clean_text(request.data["content"]):
            try:
                create_board_comment_data(author, board_id, request.data)
                return Response({"detail": "댓글이 생성되었습니다."}, status=status.HTTP_200_OK)
            except exceptions.ValidationError as e:
                error_message = "".join([str(value) for values in e.detail.values() for value in values])
                return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 댓글을 작성 할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, comment_id):

        if check_is_it_clean_text(request.data["content"]):
            try:
                if request.user != BoardCommentModel.objects.get(id=comment_id).author:
                    return Response(
                        {"detail": "수정할 수 있는 권한이 없습니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                update_board_comment_data(request.data, comment_id)
                return Response({"detail": "댓글이 수정되었습니다."}, status=status.HTTP_200_OK)
            except BoardCommentModel.DoesNotExist:
                return Response(
                    {"detail": "해당 댓글을 찾을 수 없습니다."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except exceptions.ValidationError as e:
                error_message = "".join([str(value) for values in e.detail.values() for value in values])
                return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"detail": "부적절한 내용이 담겨있어 댓글을 수정 할 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, comment_id=0):

        try:
            delete_board_comment_data(comment_id, request.user.id)
            return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except BoardCommentModel.DoesNotExist:
            return Response({"detail": "댓글이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        except TypeError:
            return Response({"detail": "comment_id가 비어있습니다."}, status=status.HTTP_404_NOT_FOUND)


class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        author = request.user

        search_type = request.query_params.get("search_type")
        search_word = request.query_params.get("search_word")

        try:
            page_num = int(request.query_params.get("page_num"))
        except ValueError:
            return Response({"detail": "게시판을 조회할 수 없습니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            searched_board_ids, total_count = get_searched_data(
                search_word=search_word, search_type=search_type, search_index="mail_box", page_num=page_num
            )
        except ValueError as e:
            return Response({"detail": e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        except IndexError:
            return Response({"detail": "검색된 값이 없습니다. 다른 검색어로 다시 검색해주세요."}, status=status.HTTP_404_NOT_FOUND)

        try:
            query_for_search = Q(id__in=searched_board_ids)
            paginated_boards = get_paginated_board_data(page_num=page_num, query=query_for_search, author=author)
        except exceptions.ValidationError as e:
            error = "".join([str(value) for values in e.detail.values() for value in values])
            return Response({"detail": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_profile_data = get_user_profile_data(author)
        except UserProfileModel.DoesNotExist:
            return Response({"detail": "잘못된 접근입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except MongleGrade.DoesNotExist:
            return Response({"detail": "잘못된 접근입니다. 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "boards": paginated_boards,
                "total_count": total_count,
                "user_profile_data": user_profile_data,
            },
            status=status.HTTP_200_OK,
        )
