from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import unsmile_filtering
from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import RequestMessageSerializer, WorryBoardSerializer


# Create your views here.
class WorryBoardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        category = int(self.request.query_params.get("category"))
        page_num = int(self.request.query_params.get("page_num"))
        if category == 0:
            worry_board_list = WorryBoardModel.objects.all().order_by("-create_date")[
                10 * (page_num - 1) : 10 + 10 * (page_num - 1)
            ]
            total_count = WorryBoardModel.objects.all().count()

        else:
            worry_board_list = WorryBoardModel.objects.filter(
                category=category
            ).order_by("-create_date")[10 * (page_num - 1) : 10 + 10 * (page_num - 1)]
            total_count = WorryBoardModel.objects.filter(category=category).count()

        return Response(
            {
                "boards": WorryBoardSerializer(
                    worry_board_list, many=True, context={"request": request}
                ).data,
                "total_count": total_count,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        filtering_sys = unsmile_filtering.post_filtering
        result = filtering_sys.unsmile_filter(request.data["content"])
        request.data["author"] = request.user.id
        if result["label"] == "clean":
            create_worry_board_serializer = WorryBoardSerializer(data=request.data)
            if create_worry_board_serializer.is_valid(raise_exception=True):
                create_worry_board_serializer.save()
                return Response(
                    {"message": "고민 게시글을 게시하였습니다."}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"message": "게시에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"message": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, worry_board_id):
        update_worry_board = WorryBoardModel.objects.get(id=worry_board_id)
        filtering_sys = unsmile_filtering.post_filtering
        result = filtering_sys.unsmile_filter(request.data["content"])
        if result["label"] == "clean":
            update_worry_board_serializer = WorryBoardSerializer(
                update_worry_board, data=request.data, partial=True
            )
            update_worry_board_serializer.is_valid(raise_exception=True)
            update_worry_board_serializer.save()
            return Response({"message": "고민 게시글이 수정되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, worry_board_id):
        delete_worry_board = WorryBoardModel.objects.get(id=worry_board_id)
        if delete_worry_board:
            delete_worry_board.delete()
            return Response({"message": "고민 게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        return Response({"message": "삭제에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)


class RequestMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, case):
        author = int(self.request.query_params.get("user_id"))
        if case == "sended":
            request_message = RequestMessageModel.objects.filter(author=author)

        elif case == "recieved":
            request_message = RequestMessageModel.objects.filter(
                worry_board__author=author
            )
        return Response(
            {
                "request_message": RequestMessageSerializer(
                    request_message, many=True, context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, worry_board_id):
        filtering_sys = unsmile_filtering.post_filtering
        result = filtering_sys.unsmile_filter(request.data["content"])
        if result["label"] == "clean":
            request.data["author"] = request.user.id
            request.data["worry_board"] = worry_board_id
            create_request_message = RequestMessageSerializer(data=request.data)
            create_request_message.is_valid(raise_exception=True)
            create_request_message.save()

            # geted, created = create_request_message.get_or_create()
            # if geted:
            #     return Response(
            #         {"message": "이미 보낸 요청입니다."},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )
            # else :
            #     create_request_message.save()

            return Response(
                {"message": "게시물 작성자에게 요청하였습니다!"}, status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"message": "부적절한 내용이 담겨있어 요청을 보낼 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
