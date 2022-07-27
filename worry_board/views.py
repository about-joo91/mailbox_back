from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

import unsmile_filtering
from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import RequestMessageSerializer, WorryBoardSerializer
from worry_board.services.worry_board_service import(
    delete_request_message_data,
    get_worry_board_data,
    create_worry_board_data,
    test_is_it_clean_text,
    update_request_message_data,
    update_worry_board_data,
    update_worry_board_data_check_is_mine,
    check_is_worry_board_true,
    delete_worry_board_data,
    create_request_message_data
)

# Create your views here.
class WorryBoardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        category = int(self.request.query_params.get("category"))
        page_num = int(self.request.query_params.get("page_num"))
        worry_board_list, total_count = get_worry_board_data(page_num, category)

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
        author_id = request.user.id
        create_worry_board_data(request.data, author_id)
        return Response(
            {"detail": "고민 게시글을 게시하였습니다."}, status=status.HTTP_200_OK
        )
        # return Response(
        #     {"detail": "게시에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST
        # )

        # return Response(
        #     {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )

    def put(self, request, worry_board_id):

        update_worry_board_data(worry_board_id, request.data)
        return Response({"detail": "고민 게시글이 수정되었습니다."}, status=status.HTTP_200_OK)
        # return Response(
        #         {"detail": "존재하지 않는 게시물입니다."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        # return Response({"detail": "수정에 실패하였습니다."}, status=status.HTTP_200_OK)
        # return Response(
        #     {"detail": "부적절한 내용이 담겨있어 게시글을 수정 할 수 없습니다"},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )
        # return Response(
        #         {"detail": "자기가 작성하지 않은 게시물은 수정이 불가합니다."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

    def delete(self, request, worry_board_id):
        try : 
            delete_worry_board_data(worry_board_id, request.user.id)
            return Response({"detail": "고민 게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except:
            return Response({"detail": "삭제에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)


class RequestMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    """
    보내거나 받은 request_message를 조회하는 view
    """
    def get(self, request, case):
        page_num = int(self.request.query_params.get("page_num"))
        author = request.user
        if case == "sended":
            request_message = RequestMessageModel.objects.filter(author=author).order_by("-create_date")
        elif case == "recieved":
            request_message = RequestMessageModel.objects.filter(worry_board__author=author).order_by("-create_date")
        total_count = request_message.count()
        return Response(
            {
                "request_message": RequestMessageSerializer(
                    request_message, many=True, context={"request": request}
                ).data,
                "total_count" : total_count
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, worry_board_id):
        """
        request 요청을 보내는 view
        """
        
        author = request.user
        create_request_message_data(request.user, worry_board_id, request.data["request_message"])  
        return Response({"detail": "게시물 작성자에게 요청하였습니다!"}, status=status.HTTP_200_OK)
        
        # return Response(
        # {"detail": "존재하지 않는 게시물입니다."},
        # status=status.HTTP_400_BAD_REQUEST)
        
        
        # return Response({"detail" : "내가 작성한 worry_board에는 요청할 수 없습니다"}, status=status.HTTP_400_BAD_REQUEST)
        # return Response(
        #     {"detail": "이미 보낸 요청입니다."},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )
        

        # return Response(
        #     {"detail": "부적절한 내용이 담겨있어 요청을 보낼 수 없습니다."},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )
    
    def put(self, request, request_message_id):
        update_request_message_data(request.data, request_message_id )
        return Response({"detail": "요청 메세지가 수정되었습니다."}, status=status.HTTP_200_OK)

    def delete(self, request, request_message_id):
        delete_request_message_data(request_message_id)
        return Response({"detail": "요청 메세지 삭제되었습니다."}, status=status.HTTP_200_OK)
        # return Response({"detail": "삭제에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
