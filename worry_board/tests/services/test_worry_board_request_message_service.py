from django.test import TestCase
from rest_framework.exceptions import ValidationError

from main_page.models import WorryCategory
from user.models import User as UserModel
from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.models import RequestStatus as RequestStatusModel
from worry_board.models import WorryBoard as WorryBoardModel
from worry_board.services.worry_board_request_message_service import (
    accept_request_message_data,
    create_request_message_data,
    delete_request_message_data,
    disaccept_request_message_data,
    get_paginated_request_message_data,
    update_request_message_data,
)
from worry_board.services.worry_board_service import check_is_it_clean_text


class TestWorryBoardRequestMessageService(TestCase):
    """
    Worry_Board의 Request_Message 서비스 함수들을 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        user = UserModel.objects.create(username="ko", nickname="ko")
        not_author_user = UserModel.objects.create(username="not_author_user", nickname="not_author_user")
        category = WorryCategory.objects.create(cate_name="일상")
        user_board = WorryBoardModel.objects.create(author=user, category=category, content="test_worry_board")

        RequestStatusModel.objects.create(status="요청")
        cancle_request_status = RequestStatusModel.objects.create(status="요청취소")
        RequestStatusModel.objects.create(status="수락됨")
        RequestStatusModel.objects.create(status="반려됨")
        RequestMessageModel.objects.create(
            author=not_author_user, worry_board=user_board, request_status=cancle_request_status
        )

    def test_when_success_get_paginated_request_message_data(self) -> None:
        """
        pagenation을 통하여 내가 보내거나 받은 request_message를 가져오는 함수에 대한 검증
        """
        page_num = 1
        user = UserModel.objects.get(username="ko")
        worry_board = WorryBoardModel.objects.get(content="test_worry_board")
        case = "sended"
        RequestMessageModel.objects.create(author=user, worry_board=worry_board)
        with self.assertNumQueries(1):
            paginated_request_message, total_count = get_paginated_request_message_data(page_num, case, user)

        self.assertEqual(1, total_count)
        self.assertEqual(
            WorryBoardModel.objects.all()[0].id,
            WorryBoardModel.objects.get(author=user).id,
        )
        self.assertEqual(
            paginated_request_message[0]["id"],
            RequestMessageModel.objects.get(author=user).id,
        )

    def test_when_success_create_request_message_data(self) -> None:
        """
        request_message_data를 생성하는 함수에 대한 검증
        """

        worry_board = WorryBoardModel.objects.get(content="test_worry_board")
        user = UserModel.objects.get(username="ko")
        request_message_data = {"request_message": "request_message 생성중"}
        if check_is_it_clean_text(request_message_data["request_message"]):
            create_request_message_data(
                author=user,
                worry_board_id=worry_board.id,
                request_message=request_message_data,
            )

        self.assertEqual(
            RequestMessageModel.objects.all().last().id,
            RequestMessageModel.objects.get(author=user).id,
        )

    def test_when_post_including_swear_word_in_create_request_message_data(
        self,
    ) -> None:
        """
        request_message_data를 생성하는 함수에 대한 검증
        case : 욕설이 포함되어 있을 때
        """
        user = UserModel.objects.get(username="ko")
        worry_board = WorryBoardModel.objects.get(content="test_worry_board")
        request_message_data = {"request_message": "바보같은놈"}
        if check_is_it_clean_text(request_message_data["request_message"]):
            create_request_message_data(
                author=user,
                worry_board_id=worry_board.id,
                request_message=request_message_data,
            )

        with self.assertRaises(RequestMessageModel.DoesNotExist):
            RequestMessageModel.objects.get(author=user).id

    def test_when_worry_board_does_not_exist_in_create_request_message_data(
        self,
    ) -> None:
        """
        request_message_data를 생성하는 함수에 대한 검증
        case : worry_baord가 없을 경우
        """
        user = UserModel.objects.get(username="ko")
        request_message_data = {"request_message": "worry_board_none"}
        if check_is_it_clean_text(request_message_data["request_message"]):
            with self.assertRaises(WorryBoardModel.DoesNotExist):
                create_request_message_data(author=user, worry_board_id=10, request_message=request_message_data)

        with self.assertRaises(RequestMessageModel.DoesNotExist):
            RequestMessageModel.objects.get(author=user).id

    def test_when_over_request_message_lengths_180_in_create_request_message_data(
        self,
    ) -> None:
        """
        request_message_data를 생성하는 함수에 대한 검증
        case : request_message의 제한수인 180을 넘겼을 경우
        """
        user = UserModel.objects.get(username="ko")
        worry_board = WorryBoardModel.objects.get(content="test_worry_board")
        create_data = {"request_message": str("A" * 190)}

        with self.assertRaises(ValidationError):
            if check_is_it_clean_text(create_data["request_message"]):
                create_request_message_data(
                    author=user,
                    worry_board_id=worry_board.id,
                    request_message=create_data,
                )

    def test_when_success_update_request_message_data(self) -> None:
        """
        request_message_data를 수정하는 함수에 대한 검증
        """

        user = UserModel.objects.get(username="ko")
        worry_board = WorryBoardModel.objects.get(content="test_worry_board")
        create_request_message = RequestMessageModel.objects.create(
            author=user, worry_board=worry_board, request_message="test"
        )

        request_message_data = {"request_message": "request_message 생성중"}

        if check_is_it_clean_text(request_message_data["request_message"]):
            update_request_message_data(
                for_update_data=request_message_data,
                request_message_id=create_request_message.id,
            )

        self.assertEqual(create_request_message.id, RequestMessageModel.objects.get(author=user).id)
        self.assertEqual(
            request_message_data["request_message"],
            RequestMessageModel.objects.get(author=user).request_message,
        )

    def test_when_post_including_swear_word_in_update_request_message_data(
        self,
    ) -> None:
        """
        request_message를 수정하는 함수가
        욕설을 포함하였을 경우에 대한 검증
        """

        user = UserModel.objects.get(username="ko")
        worry_board = WorryBoardModel.objects.get(content="test_worry_board")
        create_request_message = RequestMessageModel.objects.create(
            author=user, worry_board=worry_board, request_message="test"
        )

        request_message_data = {"request_message": "바보같은놈"}

        if check_is_it_clean_text(request_message_data["request_message"]):
            update_request_message_data(
                for_updata_date=request_message_data,
                request_message_id=create_request_message.id,
            )

        with self.assertRaises(RequestMessageModel.DoesNotExist):
            RequestMessageModel.objects.get(request_message="바보같은놈")

    def test_when_worry_board_does_not_exist_in_update_request_message_data(self) -> None:
        """
        request_message_data를 수정하는 함수에 대한 검증
        case : 해당 request_message가 없을 경우
        """
        request_message_data = {"request_message": "request_message 생성중"}

        with self.assertRaises(RequestMessageModel.DoesNotExist):
            if check_is_it_clean_text(request_message_data["request_message"]):
                update_request_message_data(
                    for_update_data=request_message_data,
                    request_message_id=9999,
                )

    def test_when_over_request_message_lengths_180_in_update_request_message_data(self) -> None:
        """
        request_message_data를 수정하는 함수에 대한 검증
        case : 글자 제한수 180을 넘었을 경우
        """

        user = UserModel.objects.get(username="ko")
        worry_board = WorryBoardModel.objects.get(content="test_worry_board")
        create_request_message = RequestMessageModel.objects.create(
            author=user, worry_board=worry_board, request_message="test"
        )
        request_message_data = {"request_message": str("A" * 190)}

        with self.assertRaises(ValidationError):
            if check_is_it_clean_text(request_message_data["request_message"]):
                update_request_message_data(
                    for_update_data=request_message_data,
                    request_message_id=create_request_message.id,
                )

    def test_when_success_delete_request_message_data(self) -> None:
        """
        request_message_data를 삭제하는 함수에 대한 검증
        """
        user = UserModel.objects.get(username="ko")
        worry_board = WorryBoardModel.objects.get(content="test_worry_board")
        create_request_message = RequestMessageModel.objects.create(
            author=user, worry_board=worry_board, request_message="test"
        )

        delete_request_message_data(request_message_id=create_request_message.id)

        self.assertEqual(1, RequestMessageModel.objects.count())

    def test_when_worry_board_does_not_exist_in_delete_request_message_data(self) -> None:
        """
        request_message_data를 삭제하는 함수에 대한 검증
        case : 삭제할 request_message가 없을 경우
        """

        with self.assertRaises(RequestMessageModel.DoesNotExist):
            delete_request_message_data(request_message_id=9999)

    def test_accept_request_message_data(self) -> None:
        """
        받은 Request_message를 수락하는 함수에 대한 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        not_author_user = UserModel.objects.get(username="not_author_user", nickname="not_author_user")
        user_board = WorryBoardModel.objects.get(author=user, content="test_worry_board")

        user_received_request_message = RequestMessageModel.objects.get(author=not_author_user, worry_board=user_board)
        accept_request_message_data(user_received_request_message.id)

        self.assertEqual(
            "수락됨", RequestMessageModel.objects.get(author=not_author_user, worry_board=user_board).request_status.status
        )

    def test_when_request_message_does_not_exixt_in_accept_request_message_data(self) -> None:
        """
        받은 Request_message를 수락하는 함수에 대한 검증
        case : request_message가 존재하지 않을 경우
        """

        with self.assertRaises(RequestMessageModel.DoesNotExist):
            accept_request_message_data(-1)

    def test_when_use_none_request_status_in_accept_request_message_data(self) -> None:
        """
        받은 Request_message를 수락하는 함수에 대한 검증
        case : 수락됨이라는 status가 존재하지 않을 경우
        """
        RequestStatusModel.objects.get(status="수락됨").delete()

        user = UserModel.objects.get(username="ko", nickname="ko")
        not_author_user = UserModel.objects.get(username="not_author_user", nickname="not_author_user")
        user_board = WorryBoardModel.objects.get(author=user, content="test_worry_board")

        user_received_request_message = RequestMessageModel.objects.get(author=not_author_user, worry_board=user_board)

        with self.assertRaises(RequestStatusModel.DoesNotExist):
            accept_request_message_data(user_received_request_message.id)

    def test_when_already_disaccepted_in_accept_request_message_data(self) -> None:
        """
        받은 Request_message를 수락하는 함수에 대한 검증
        case : 이미 반려된 request_message인 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        not_author_user = UserModel.objects.get(username="not_author_user", nickname="not_author_user")
        user_board = WorryBoardModel.objects.get(author=user, content="test_worry_board")
        disaccepted_request_status = RequestStatusModel.objects.get(status="반려됨")
        user_received_request_message = RequestMessageModel.objects.create(
            author=not_author_user, worry_board=user_board, request_status=disaccepted_request_status
        )
        accept_request_message_data(user_received_request_message.id)

        self.assertEqual(
            "수락됨",
            RequestMessageModel.objects.filter(author=not_author_user, worry_board=user_board)
            .last()
            .request_status.status,
        )

    def test_disaccept_request_message_data(self) -> None:
        """
        받은 Request_message를 거절하는 함수에 대한 검증
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        not_author_user = UserModel.objects.get(username="not_author_user", nickname="not_author_user")
        user_board = WorryBoardModel.objects.get(author=user, content="test_worry_board")

        user_received_request_message = RequestMessageModel.objects.get(author=not_author_user, worry_board=user_board)
        disaccept_request_message_data(user_received_request_message.id)

        self.assertEqual(
            "반려됨", RequestMessageModel.objects.get(author=not_author_user, worry_board=user_board).request_status.status
        )

    def test_when_request_message_does_not_exixt_in_disaccept_request_message_data(self) -> None:
        """
        받은 Request_message를 거절하는 함수에 대한 검증
        case : request_message가 존재하지 않을 경우
        """
        with self.assertRaises(RequestMessageModel.DoesNotExist):
            disaccept_request_message_data(-1)

    def test_when_already_accepted_in_disaccept_request_message_data(self) -> None:
        """
        받은 Request_message를 거절하는 함수에 대한 검증
        case : 이미 수락된 request_message인 경우
        """
        user = UserModel.objects.get(username="ko", nickname="ko")
        not_author_user = UserModel.objects.get(username="not_author_user", nickname="not_author_user")
        user_board = WorryBoardModel.objects.get(author=user, content="test_worry_board")
        accepted_request_status = RequestStatusModel.objects.get(status="수락됨")
        user_received_request_message = RequestMessageModel.objects.create(
            author=not_author_user, worry_board=user_board, request_status=accepted_request_status
        )

        disaccept_request_message_data(user_received_request_message.id)
        self.assertEqual(
            "반려됨",
            RequestMessageModel.objects.filter(author=not_author_user, worry_board=user_board)
            .last()
            .request_status.status,
        )
