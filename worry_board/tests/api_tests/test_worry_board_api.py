import json

from rest_framework.test import APIClient, APITestCase

from main_page.models import WorryCategory as WorryCategoryModel
from user.models import User as UserModel
from worry_board.models import RequestStatus as RequestStatusModel
from worry_board.models import WorryBoard as WorryBoardModel


class TestWorryBoardAPI(APITestCase):
    """
    WorryBoard의 API를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):
        user = UserModel.objects.create(username="test", nickname="test")
        category = WorryCategoryModel.objects.create(cate_name="가족")
        WorryBoardModel.objects.create(author=user, category=category, content="APItest")
        RequestStatusModel.objects.create(status="요청")

    def test_get_worry_board_API(self) -> None:
        """
        WorryBoard의 get함수를 검증하는 함수
        """
        client = APIClient()

        user = UserModel.objects.get(username="test")
        client.force_authenticate(user=user)

        url = "/worry_board/?category=0&page_num=1"
        response = client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual("APItest", result["boards"][0]["content"])
        self.assertEqual(result["total_count"], 1)

    def test_when_is_user_is_unauthenticated_in_get_worry_board_API(self) -> None:
        """
        WorryBoardView의 get 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 조회하는 경우
        """
        client = APIClient()

        url = "/worry_board/?category=0&page_num=1"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_parameter_does_not_exist_in_get_worry_board_API(self) -> None:
        """
        WorryBoardView의 get 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")

        client.force_authenticate(user=user)

        url = "/worry_board/"
        response = client.get(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "게시판을 조회할 수 없습니다. 다시 시도해주세요.")

    def test_post_worry_board_API(self) -> None:
        """
        WorryBoardView의 post 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        category = WorryCategoryModel.objects.get(cate_name="가족")
        request_data = {
            "category": category.id,
            "content": "new_post",
        }

        client.force_authenticate(user=user)
        url = "/worry_board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(
            WorryBoardModel.objects.all().count(),
            WorryBoardModel.objects.filter(author=user).count(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "고민 게시글을 게시하였습니다.")

    def test_when_unauthenticated_user_in_post_worry_board_API(self) -> None:
        """
        WorryBoardView의 post 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 post하는 경우
        """
        category = WorryCategoryModel.objects.get(cate_name="가족")
        client = APIClient()
        request_data = {"category": category.id, "content": "new_post"}

        url = "/worry_board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_caregory_does_not_exist_in_post_worry_board_API(self) -> None:
        """
        WorryBoardView의 post 함수를 검증하는 함수
        case : 카테고리가 없는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        request_data = {"content": "new_post"}

        client.force_authenticate(user=user)
        url = "/worry_board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(result["detail"], "이 필드는 필수 항목입니다.")

    def test_when_wrong_caregory_in_post_worry_board_API(self) -> None:
        """
        WorryBoardView의 post 함수를 검증하는 함수
        case : 카테고리가 잘못된 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        request_data = {"category": 10, "content": "new_post"}

        client.force_authenticate(user=user)
        url = "/worry_board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")

        self.assertEqual(400, response.status_code)

    def test_when_word_over_90_text_post_worry_board_API(self) -> None:
        """
        WorryBoardView의 post 함수를 검증하는 함수
        case : 제한된 글자 수 90을 넘은 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        category = WorryCategoryModel.objects.get(cate_name="가족")
        request_data = {
            "category": category.id,
            "content": str("A" * 100),
        }

        client.force_authenticate(user=user)
        url = "/worry_board/"
        response = client.post(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "이 필드의 글자 수가 90 이하인지 확인하십시오.")

    def test_put_worry_board_API(self) -> None:
        """
        WorryBoardView의 put 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        worry_board = WorryBoardModel.objects.get(content="APItest")
        category = WorryCategoryModel.objects.get(cate_name="가족")
        request_data = {"category": category.id, "content": "update_post"}

        client.force_authenticate(user=user)
        url = "/worry_board/" + str(worry_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(WorryBoardModel.objects.filter(author=user)[0].content, "update_post")
        self.assertEqual(worry_board.id, WorryBoardModel.objects.filter(author=user)[0].id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "고민 게시글이 수정되었습니다.")

    def test_when_unauthenticated_user_put_worry_board_API(self) -> None:
        """
        WorryBoardView의 put 함수를 검증하는 함수
        case : 로그인하지 않은 사용자가 put하는 경우
        """

        client = APIClient()
        user = UserModel.objects.get(username="test")
        worry_board = WorryBoardModel.objects.get(content="APItest")
        category = WorryCategoryModel.objects.get(cate_name="가족")
        request_data = {"category": category.id, "content": "update_post"}

        url = "/worry_board/" + str(worry_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(WorryBoardModel.objects.filter(author=user)[0].content, "APItest")
        self.assertEqual(response.status_code, 401)

        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_not_author_put_worry_board_API(self) -> None:
        """
        WorryBoardView의 put 함수를 검증하는 함수
        case : 해당 게시물을 작성한 사용자가 아닌 사용자가 수정을 하려는 경우
        """

        client = APIClient()
        not_author = UserModel.objects.create(username="not_author", nickname="not_author")
        user = UserModel.objects.get(username="test")
        category = WorryCategoryModel.objects.get(cate_name="가족")

        not_author_worry_board = WorryBoardModel.objects.create(author=not_author, category=category, content="APItest")

        request_data = {"category": category.id, "content": "update_post"}
        client.force_authenticate(user=user)
        url = "/worry_board/" + str(not_author_worry_board.id)

        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(WorryBoardModel.objects.filter(author=not_author)[0].content, "APItest")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "자기가 작성하지 않은 게시물은 수정이 불가합니다.")

    def test_when_parameter_does_not_exist_in_put_worry_board_API(self) -> None:
        """
        WorryBoardView의 put 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우 (worry_board가 특정되지 않을 경우)
        """

        client = APIClient()
        user = UserModel.objects.get(username="test")
        category = WorryCategoryModel.objects.get(cate_name="가족")

        request_data = {"category": category.id, "content": "update_post"}

        client.force_authenticate(user=user)
        url = "/worry_board/"

        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "worry_board_id가 비어있습니다.")

    def test_when_content_over_90_text_put_worry_board_API(self) -> None:
        """
        WorryBoardView의 put 함수를 검증하는 함수
        case : 제한된 텍스트 90을 넘었을 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        worry_board = WorryBoardModel.objects.get(content="APItest")
        category = WorryCategoryModel.objects.get(cate_name="가족")
        request_data = {"category": category.id, "content": str("A" * 130)}

        client.force_authenticate(user=user)
        url = "/worry_board/" + str(worry_board.id)
        response = client.put(url, data=json.dumps(request_data), content_type="application/json")
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "이 필드의 글자 수가 90 이하인지 확인하십시오.")

    def test_delete_worry_board_API(self) -> None:
        """
        WorryBoardView의 delete 함수를 검증하는 함수
        """

        client = APIClient()
        user = UserModel.objects.get(username="test")
        worry_board = WorryBoardModel.objects.get(content="APItest")
        client.force_authenticate(user=user)
        url = "/worry_board/" + str(worry_board.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(WorryBoardModel.objects.filter(author=user).count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["detail"], "고민 게시글이 삭제되었습니다.")

    def test_when_unauthenticated_user_delete_worry_board_API(self) -> None:
        """
        WorryBoardView의 delete 함수를 검증하는 함수
        case: 로그인하지 않은 사용자가 게시물을 삭제하려는 경우
        """
        client = APIClient()
        worry_board = WorryBoardModel.objects.get(content="APItest")
        url = "/worry_board/" + str(worry_board.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(WorryBoardModel.objects.all().count(), 1)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(result["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_when_not_author_delete_board_content(self) -> None:
        """
        WorryBoardView의 delete 함수를 검증하는 함수
        case: 해당 게시물을 작성하지 않은 사람이 게시물을 삭제하려는 경우
        """
        client = APIClient()
        worry_board = WorryBoardModel.objects.get(content="APItest")
        not_author = UserModel.objects.create(username="not_author", nickname="not_author")

        client.force_authenticate(user=not_author)
        url = "/worry_board/" + str(worry_board.id)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(WorryBoardModel.objects.all().count(), 1)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "유저의 고민 게시글과 일치하는 게시글이 없습니다.")

    def test_when_parameter_does_not_exist_in_delete_worry_board_API(self) -> None:
        """
        WorryBoardView의 delete 함수를 검증하는 함수
        case : 빈파라미터를 넣은 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")

        client.force_authenticate(user=user)
        url = "/worry_board/"
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(result["detail"], "worry_board_id가 비어있습니다.")

    def test_when_post_does_not_exist_in_delete_worry_board_API(self) -> None:
        """
        WorryBoardView의 delete 함수를 검증하는 함수
        case : 존재하지 않는 게시물을 삭제하려는 경우
        """
        client = APIClient()
        user = UserModel.objects.get(username="test")
        client.force_authenticate(user=user)
        url = "/worry_board/" + str(9999)
        response = client.delete(url)
        result = response.json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(result["detail"], "유저의 고민 게시글과 일치하는 게시글이 없습니다.")
