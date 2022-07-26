from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from unsmile_filtering import pipe
from worry_board.models import WorryBoard as WorryBoardModel, RequestMessage as RequestMessageModel
from worry_board.serializers import WorryBoardSerializer, RequestMessageSerializer


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
        request.data["author"] = request.user.id
        result = pipe(request.data["content"])[0]
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
        update_worry_board_serializer = WorryBoardSerializer(
            update_worry_board, data=request.data, partial=True
        )
        update_worry_board_serializer.is_valid(raise_exception=True)
        update_worry_board_serializer.save()
        return Response({"message": "고민 게시글이 수정되었습니다."}, status=status.HTTP_200_OK)

    def delete(self, request, worry_board_id):
        delete_worry_board = WorryBoardModel.objects.get(id=worry_board_id)
        if delete_worry_board:
            delete_worry_board.delete()
            return Response({"message": "고민 게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        return Response({"message": "삭제에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)



class RequestMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    """
    보내거나 받은 request_message를 조회하는 view
    """
    def get(self, request, case):
        author = int(self.request.query_params.get("user_id"))
        if case == "sended":
            request_message = RequestMessageModel.objects.filter(author=author)
        
        elif case == "recieved":
            request_message = RequestMessageModel.objects.filter(worry_board__author=author)
        return Response(
            {
                "request_message": RequestMessageSerializer(
                    request_message, many=True, context={"request": request}
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, worry_board_id):
        """
        request 요청을 보내는 view
        """
        result = pipe(request.data["request_message"])[0]
        if result["label"] == "clean":
            author = request.user
            check_my_worry_board = WorryBoardModel.objects.filter(id=worry_board_id)
            print(check_my_worry_board)
            if check_my_worry_board:
                request_message = request.data['request_message']
                if check_my_worry_board.author == author:
                    return Response({"message" : "내가 작성한 worry_board에는 요청할 수 없습니다"}, status=status.HTTP_400_BAD_REQUEST)
                
                geted_request_message, created_request_message = RequestMessageModel.objects.get_or_create(author=author, worry_board_id=worry_board_id)
                if created_request_message:
                    new_request_message = RequestMessageModel.objects.create(
                        author = author,
                        worry_board_id = worry_board_id,
                        request_message = request_message
                    )
                    new_request_message.save()
                    return Response({"message": "게시물 작성자에게 요청하였습니다!"}, status=status.HTTP_200_OK)

                return Response(
                    {"message": "이미 보낸 요청입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {"message": "존재하지 않는 게시물입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"message": "부적절한 내용이 담겨있어 요청을 보낼 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    
    def put(self, request, request_message_id):
        update_request_message = RequestMessageModel.objects.get(id=request_message_id)
        update_request_message_serializer = RequestMessageSerializer(
            update_request_message, data=request.data, partial=True
        )
        update_request_message_serializer.is_valid(raise_exception=True)
        update_request_message_serializer.save()
        return Response({"message": "요청 메세지가 수정되었습니다."}, status=status.HTTP_200_OK)

    def delete(self, request, request_message_id):
        delete_request_message = RequestMessageModel.objects.get(id=request_message_id)
        if delete_request_message:
            delete_request_message.delete()
            return Response({"message": "요청 메세지 삭제되었습니다."}, status=status.HTTP_200_OK)
        return Response({"message": "삭제에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
