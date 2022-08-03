import json

from rest_framework.test import APIClient, APITestCase

from main_page.models import WorryCategory as WorryCategoryModel
from user.models import User as UserModel
from worry_board.models import RequestMessage as RequestMessageModel
from worry_board.models import RequestStatus as RequestStatusModel
from worry_board.models import WorryBoard as WorryBoardModel


class TestRequestMessageAPI(APITestCase):
    """
    RequestMessage의 API를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        user = UserModel.objects.create(username="test", nickname="test")
        not_author_user = UserModel.objects.create(username="not_author", nickname="not_author")
        category = WorryCategoryModel.objects.create(cate_name="가족")

        user_worry_board = WorryBoardModel.objects.create(author=user, category=category, content="APItest")
        not_author_user_worry_board = WorryBoardModel.objects.create(
            author=not_author_user, category=category, content="APItest"
        )
        WorryBoardModel.objects.create(
            author=not_author_user,
            category=category,
            content="user가 new_request_message를 보낼 worry_board",
        )
        RequestStatusModel.objects.create(status="요청")
        cancle_request_status = RequestStatusModel.objects.create(status="요청취소")
        RequestStatusModel.objects.create(status="수락됨")
        RequestStatusModel.objects.create(status="반려됨")

        RequestMessageModel.objects.create(
            author=user,
            worry_board=not_author_user_worry_board,
            request_message="user기준 보낸 메세지",
            request_status=cancle_request_status,
        )
        RequestMessageModel.objects.create(
            author=not_author_user,
            worry_board=user_worry_board,
            request_message="user기준 받은 메세지",
            request_status=cancle_request_status,
        )

    def test_get_sended_request_message_API(self) -> None:
        """
        RequestMessage의 get 함수를 검증하는 함수
        case : 내가 보낸 메세지
        """
        client = APIClient()

        user = UserModel.objects.get(username="test")
        client.force_authenticate(user=user)

        url = "/worry_board/request/sended"
        response = client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual("user기준 보낸 메세지", response.json()["request_message"][0]["request_message"])
        self.assertEqual(result["total_count"], 1)

    def test_when_is_user_is_unauthenticated_in_get_sended_request_message_API(
        self,
    ) -> None:
        """
        RequestMessage의 get 함수를 검증하는 함수
        case1 : 내가 보낸 메세지
        case2 : 로그인하지 않은 사용자가 조회하는 경우
        """
        client = APIClient()

        url = "/worry_board/request/sended"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_get_received_request_message_API(self) -> None:
        """
        RequestMessage의 get 함수를 검증하는 함수
        case : 내가 받은 메세지
        """
        client = APIClient()

        user = UserModel.objects.get(username="test")
        client.force_authenticate(user=user)

        url = "/worry_board/request/received"
        response = client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual("user기준 받은 메세지", response.json()["request_message"][0]["request_message"])
        self.assertEqual(result["total_count"], 1)

    def test_when_is_user_is_unauthenticated_in_get_received_request_message_API(
        self,
    ) -> None:
        """
        RequestMessage의 get 함수를 검증하는 함수
        case1 : 내가 받은 메세지
        case2 : 로그인하지 않은 사용자가 조회하는 경우
        """
        client = APIClient()

        url = "/worry_board/request/received"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_post_request_message_API(self) -> None:
        """
        RequestMessage의 post 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_worry_board = WorryBoardModel.objects.get(content="user가 new_request_message를 보낼 worry_board")
        request_data = {"request_message": "new_request_message"}

        client.force_authenticate(user=user)
        url = "/worry_board/request/" + str(target_worry_board.id)
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(
            2,
            RequestMessageModel.objects.filter(author=user).count(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "게시물 작성자에게 요청하였습니다!")

    def test_when_worry_wrong_board_in_post_request_message_API(self) -> None:
        """
        RequestMessage의 post 함수를 검증하는 함수
        case : 존재하지 않는 worry_board가 들어갔을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        request_data = {"request_message": "new_request_message"}

        client.force_authenticate(user=user)
        url = "/worry_board/request/999999"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "worry_board가 존재하지 않습니다.")

    def test_when_already_requested_in_post_request_message_API(self) -> None:
        """
        RequestMessage의 post 함수를 검증하는 함수
        case : 해당 worry_board에 이미 내가 요청을 한 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        not_author_user = UserModel.objects.get(username="not_author")
        user_already_requested_worry_board = WorryBoardModel.objects.filter(author=not_author_user).filter(
            requestmessage__author=user
        )
        request_data = {"request_message": "new_request_message"}

        client.force_authenticate(user=user)
        url = "/worry_board/request/" + str(user_already_requested_worry_board[0].id)
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "이미 보낸 요청입니다.")

    def test_when_requested_target_user_is_me_in_post_request_message_API(self) -> None:
        """
        RequestMessage의 post 함수를 검증하는 함수
        ase : 해당 worry_board의 작성자가 자신일 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_worry_board = WorryBoardModel.objects.get(author=user)
        request_data = {"request_message": "new_request_message"}

        client.force_authenticate(user=user)
        url = "/worry_board/request/" + str(target_worry_board.id)
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "내가 작성한 게시물에는 요청할 수 없습니다.")

    def test_when_unauthenticated_user_post_request_message_API(self) -> None:
        """
        RequestMessage의 post 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 post하는 경우
        """
        client = APIClient()

        target_worry_board = WorryBoardModel.objects.get(content="user가 new_request_message를 보낼 worry_board")
        request_data = {"request_message": "new_request_message"}

        url = "/worry_board/request/" + str(target_worry_board.id)
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_including_swear_word_in_post_request_message_API(self) -> None:
        """
        RequestMessage의 post 함수를 검증하는 함수
        case : 욕설을 포함한 내용을 post하는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_worry_board = WorryBoardModel.objects.get(content="user가 new_request_message를 보낼 worry_board")
        request_data = {"request_message": "바보 멍청이"}

        client.force_authenticate(user=user)
        url = "/worry_board/request/" + str(target_worry_board.id)
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 요청을 보낼 수 없습니다.")

    def test_put_request_message_API(self) -> None:
        """
        RequestMessage의 put 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 보낸 메세지")
        request_data = {"request_message": "update_request_message"}

        client.force_authenticate(user=user)
        url = "/worry_board/request/pd/" + str(target_request_message.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "요청 메세지가 수정되었습니다.")

    def test_when_update_request_message_does_not_exist_in_put_request_message_API(
        self,
    ) -> None:
        """
        RequestMessage의 put 함수를 검증하는 함수
        case : 수정할 request_message가 없을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        request_data = {"request_message": "update_request_message"}

        client.force_authenticate(user=user)
        url = "/worry_board/request/pd/" + str(9999)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "해당 요청 메세지가 존재하지 않습니다.")

    def test_when_is_user_is_unauthenticated_in_put_request_message_API(self) -> None:
        """
        RequestMessage의 put 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 put하는 경우
        """
        client = APIClient()
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 보낸 메세지")
        request_data = {"request_message": "update_request_message"}

        url = "/worry_board/request/pd/" + str(target_request_message.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 401)

        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_including_swear_word_in_put_request_message_API(self) -> None:
        """
        RequestMessage의 put 함수를 검증하는 함수
        case : 욕설을 포함한 내용을 포함했을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 보낸 메세지")
        request_data = {"request_message": "바보 멍청이"}

        client.force_authenticate(user=user)
        url = "/worry_board/request/pd/" + str(target_request_message.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 요청을 보낼 수 없습니다.")

    def test_delete_request_message_API(self) -> None:
        """
        RequestMessage의 delete 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 보낸 메세지")

        client.force_authenticate(user=user)
        url = "/worry_board/request/pd/" + str(target_request_message.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "요청 메세지가 삭제되었습니다.")

    def test_when_delete_request_message_does_not_exiest_in_delete_request_message_API(
        self,
    ) -> None:
        """
        RequestMessage의 delete 함수를 검증하는 함수
        case : 삭제할 request_message가 없을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")

        client.force_authenticate(user=user)
        url = "/worry_board/request/pd/" + str(99999)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "해당 요청 메세지가 존재하지 않습니다.")

    def test_when_is_user_is_unauthenticated_in_delete_request_message_API(
        self,
    ) -> None:
        """
        RequestMessage의 delete 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 조회하는 경우
        """
        client = APIClient()
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 보낸 메세지")

        url = "/worry_board/request/pd/" + str(target_request_message.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_accept_request_message_API(self) -> None:
        """
        request_message를 수락,거절하는 함수를 검증하는 함수
        case1 : request_message를 수락하는 경우

        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 받은 메세지")

        client.force_authenticate(user=user)
        url = "/worry_board/request/accept/" + str(target_request_message.id) + "/accept"
        response = client.put(url)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "요청 메세지를 수락하였습니다.")

    def test_when_is_user_is_unauthenticated_in_accept_request_message_API(self) -> None:
        """
        request_message를 수락,거절하는 함수를 검증하는 함수
        case1 : request_message를 수락하는 경우
        case2 : 로그인하지 않은 사용자가 조회하는 경우
        """
        client = APIClient()
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 보낸 메세지")

        url = "/worry_board/request/accept/" + str(target_request_message.id) + "/accept"
        response = client.put(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_request_message_does_not_exist_in_accept_request_message_API(self) -> None:
        """
        request_message를 수락,거절하는 함수를 검증하는 함수
        case1 : request_message를 수락하는 경우
        case2 : 잘못된 request_message_id를 받았을 때
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")

        client.force_authenticate(user=user)
        url = "/worry_board/request/accept/" + str(99999) + "/accept"
        response = client.put(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "해당 요청은 존재하지 않습니다.")

    def test_when_does_not_my_request_message_in_accept_request_message_API(self) -> None:
        """
        request_message를 수락,거절하는 함수를 검증하는 함수
        case1 : request_message를 수락하는 경우
        case2 : 내가 받은 메세지가 아닐경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 보낸 메세지")

        client.force_authenticate(user=user)
        url = "/worry_board/request/accept/" + str(target_request_message.id) + "/accept"
        response = client.put(url)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "수락 권한이 없습니다.")

    def test_disaccept_request_message_API(self) -> None:
        """
        request_message를 수락,거절하는 함수를 검증하는 함수
        case1 : request_message를 거절하는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 받은 메세지")

        client.force_authenticate(user=user)
        url = "/worry_board/request/accept/" + str(target_request_message.id) + "/disaccept"
        response = client.put(url)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "요청 메세지를 거절하였습니다.")

    def test_when_is_user_is_unauthenticated_in_disaccept_request_message_API(self) -> None:
        """
        request_message를 수락,거절하는 함수를 검증하는 함수
        case1 : request_message를 거절하는 경우
        case2 : 로그인하지 않은 사용자가 조회하는 경우
        """
        client = APIClient()
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 받은 메세지")

        url = "/worry_board/request/accept/" + str(target_request_message.id) + "/disaccept"
        response = client.put(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_request_message_does_not_exist_in_disaccept_request_message_API(self) -> None:
        """
        request_message를 수락,거절하는 함수를 검증하는 함수
        case1 : request_message를 거절하는 경우
        case2 : 잘못된 request_message_id를 받았을 때
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")

        client.force_authenticate(user=user)
        url = "/worry_board/request/accept/" + str(9999) + "/disaccept"
        response = client.put(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "해당 요청은 존재하지 않습니다.")

    def test_when_does_not_my_request_message_in_disaccept_request_message_API(self) -> None:
        """
        request_message를 수락,거절하는 함수를 검증하는 함수
        case1 : request_message를 거절하는 경우
        case2 : 내가 받은 메세지가 아닐경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        target_request_message = RequestMessageModel.objects.get(request_message="user기준 보낸 메세지")

        client.force_authenticate(user=user)
        url = "/worry_board/request/accept/" + str(target_request_message.id) + "/disaccept"
        response = client.put(url)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "거절 권한이 없습니다.")
