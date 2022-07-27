from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.serializers import RequestMessageSerializer, WorryBoardSerializer
from worry_board.services.worry_board_service import(
    get_paginated_worry_board_data,
    create_worry_board_data,
    check_is_it_clean_text,
    update_worry_board_data,
    delete_worry_board_data,
    
)
from worry_board.services.worry_board_request_message_service import(
    get_paginated_request_message_data,
    create_request_message_data,
    update_request_message_data,
    delete_request_message_data,
)

# Create your views here.
class WorryBoardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        category = int(self.request.query_params.get("category"))
        page_num = int(self.request.query_params.get("page_num"))
        paginated_worry_board, total_count = get_paginated_worry_board_data(page_num, category)
        
        return Response(
            {
                "boards": WorryBoardSerializer(
                    paginated_worry_board, many=True, context={"request": request}
                ).data,
                "total_count": total_count,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        author = request.user
        if check_is_it_clean_text(request.data["content"]):
            create_worry_board_data(request.data, author)
            return Response(
                {"detail": "고민 게시글을 게시하였습니다."}, status=status.HTTP_200_OK
            )
        else :
            return Response(
            {"detail": "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다"},
            status=status.HTTP_400_BAD_REQUEST,
        )

        # return Response(
        #     {"detail": "게시에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST
        # )

    def put(self, request, worry_board_id):
        
        if check_is_it_clean_text(request.data["content"]):
            update_worry_board_data(worry_board_id, request.data)
            return Response({"detail": "고민 게시글이 수정되었습니다."}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "부적절한 내용이 담겨있어 게시글을 수정 할 수 없습니다"},
            status=status.HTTP_400_BAD_REQUEST,
        )
        # return Response(
        #         {"detail": "존재하지 않는 게시물입니다."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        # return Response({"detail": "수정에 실패하였습니다."}, status=status.HTTP_200_OK)
        # return Response(
        #         {"detail": "자기가 작성하지 않은 게시물은 수정이 불가합니다."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

    def delete(self, request, worry_board_id):
        author = request.user
        try : 
            delete_worry_board_data(worry_board_id, author)
            return Response({"detail": "고민 게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except WorryBoardModel.DoesNotExist:
            return Response({"detail": "게시글이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)


class RequestMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    """
    보내거나 받은 request_message를 조회하는 view
    """
    def get(self, request, case):
        
        try: 
            page_num = int(self.request.query_params.get("page_num"))
        except:
            page_num = 1
        author = request.user
        paginated_request_message, total_count = get_paginated_request_message_data(page_num, case, author)
        
        return Response(
            {
                "request_message": RequestMessageSerializer(
                    paginated_request_message, many=True, context={"request": request}
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
        check_content = request.data["request_message"]
        if check_is_it_clean_text(check_content):
            create_request_message_data(author, worry_board_id, check_content)  
            return Response({"detail": "게시물 작성자에게 요청하였습니다!"}, status=status.HTTP_200_OK)
        
        else :
            return Response(
            {"detail": "부적절한 내용이 담겨있어 요청을 보낼 수 없습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

        # return Response(
        # {"detail": "존재하지 않는 게시물입니다."},
        # status=status.HTTP_400_BAD_REQUEST)
        
        
        # return Response({"detail" : "내가 작성한 worry_board에는 요청할 수 없습니다"}, status=status.HTTP_400_BAD_REQUEST)
        # return Response(
        #     {"detail": "이미 보낸 요청입니다."},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )
        

    
    def put(self, request, request_message_id):
        for_update_data = request.data
        update_request_message_data(for_update_data.data, request_message_id )
        return Response({"detail": "요청 메세지가 수정되었습니다."}, status=status.HTTP_200_OK)

    def delete(self, request, request_message_id):
        delete_request_message_data(request_message_id)
        return Response({"detail": "요청 메세지 삭제되었습니다."}, status=status.HTTP_200_OK)
        # return Response({"detail": "삭제에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
