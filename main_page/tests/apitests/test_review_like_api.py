from rest_framework.test import APIClient, APITestCase

from main_page.models import Letter as LetterModel
from main_page.models import LetterReview as LetterReviewModel
from main_page.models import LetterReviewLike as LetterReviewLikeModel
from main_page.models import WorryCategory as WorryCategoryModel
from main_page.services.letter_service import letter_review_like_service
from user.models import User as UserModel
from worry_board.models import WorryBoard as WorryBoardModel


class TestLetterReviewPostLikeAPI(APITestCase):
    """
    ReviewLikeView의 API를 검증하는 클래스
    """

    def test_post_like_post(self) -> None:
        """
        LetterReviewLike 의 post 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="hajin", password="1234", nickname="hajin"
        )
        WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
            author_id=user.id, content="test", category_id=daily_cate.id
        )
        letter_obj = LetterModel.objects.create(
            letter_author=user,
            worryboard_id=worry_obj.id,
            title="test",
            content="test",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author=user,
            letter_id=letter_obj.id,
            content="test",
            grade=100,
        )

        client.force_authenticate(user=user)
        url = f"/main_page/review_like{letter_review_obj.id}"
        response = client.post(
            url,
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(result["detail"], "좋아요가 완료 되었습니다!!")

    def test_when_overlap_post_like(self) -> None:
        """
        LetterReviewLike 의 post 함수를 검증하는 함수
        case: 중복된 letter_review 에 좋아요를 할 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="hajin", password="1234", nickname="hajin"
        )
        WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
            author_id=user.id, content="test", category_id=daily_cate.id
        )
        letter_obj = LetterModel.objects.create(
            letter_author=user,
            worryboard_id=worry_obj.id,
            title="test",
            content="test",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author=user,
            letter_id=letter_obj.id,
            content="test",
            grade=100,
        )

        letter_review_like_service(
            letter_review_id=letter_review_obj.id, user_id=user.id
        )

        client.force_authenticate(user=user)
        url = f"/main_page/review_like{letter_review_obj.id}"
        response = client.post(
            url,
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(result["detail"], "좋아요를 이미 누르셨습니다!!")

    def test_when_user_is_unauthenticated_in_review_like_post(self) -> None:
        """
        LetterReviewLike 의 post 함수를 검증하는 함수
        case: 인증되지 않은 유저일 때
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="hajin", password="1234", nickname="hajin"
        )
        WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
            author_id=user.id, content="test", category_id=daily_cate.id
        )
        letter_obj = LetterModel.objects.create(
            letter_author=user,
            worryboard_id=worry_obj.id,
            title="test",
            content="test",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author=user,
            letter_id=letter_obj.id,
            content="test",
            grade=100,
        )

        url = f"/main_page/review_like{letter_review_obj.id}"
        response = client.post(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"]
        )

    def test_letter_reveiw_delete_like(self) -> None:
        """
        LetterReviewLike 의 delete 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="hajin", password="1234", nickname="hajin"
        )
        WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
            author_id=user.id, content="test", category_id=daily_cate.id
        )
        letter_obj = LetterModel.objects.create(
            letter_author=user,
            worryboard_id=worry_obj.id,
            title="test",
            content="test",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author=user,
            letter_id=letter_obj.id,
            content="test",
            grade=100,
        )
        target_letter_review_like_obj = LetterReviewLikeModel.objects.create(
            letter_review=letter_review_obj, user=user
        )
        target_review_like = LetterReviewLikeModel.objects.get(
            id=target_letter_review_like_obj.id
        )
        client.force_authenticate(user=user)
        url = f"/main_page/review_like{target_review_like.id}"
        response = client.delete(
            url,
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(result["detail"], "좋아요가 취소 되었습니다!!")

    def test_when_user_is_unauthenticated_in_review_like_delete(self) -> None:
        """
        LetterReviewLike 의 delete 함수를 검증하는 함수
        case: 인증되지 않은 유저일 때
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="hajin", password="1234", nickname="hajin"
        )
        WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
            author_id=user.id, content="test", category_id=daily_cate.id
        )
        letter_obj = LetterModel.objects.create(
            letter_author=user,
            worryboard_id=worry_obj.id,
            title="test",
            content="test",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author=user,
            letter_id=letter_obj.id,
            content="test",
            grade=100,
        )
        target_letter_review_like_obj = LetterReviewLikeModel.objects.create(
            letter_review=letter_review_obj, user=user
        )
        url = f"/main_page/review_like{target_letter_review_like_obj.id}"
        response = client.delete(url)
        result = response.json()
        self.assertEqual(401, response.status_code)
        self.assertEqual(
            "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"]
        )

    def test_when_not_letter_review_delete_like(self) -> None:
        """
        LetterReviewLike 의 delete 함수를 검증하는 함수
        case: 없는 리뷰 일 때
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="hajin", password="1234", nickname="hajin"
        )

        client.force_authenticate(user=user)
        url = "/main_page/review_like9999"
        response = client.delete(
            url,
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(result["detail"], "없는 리뷰 입니다.")

    def test_when_different_user_review_like_delete(self) -> None:
        """
        LetterReviewLike 의 delete 함수를 검증하는 함수
        case: 다른유저가 좋아요 를 취소 할 경우
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="hajin", password="1234", nickname="hajin"
        )
        different_user = UserModel.objects.create(
            username="different_user", password="1234", nickname="different_user"
        )
        WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
            author_id=user.id, content="test", category_id=daily_cate.id
        )
        letter_obj = LetterModel.objects.create(
            letter_author=user,
            worryboard_id=worry_obj.id,
            title="test",
            content="test",
        )
        letter_review_obj = LetterReviewModel.objects.create(
            review_author=user,
            letter_id=letter_obj.id,
            content="test",
            grade=100,
        )
        target_letter_review_like_obj = LetterReviewLikeModel.objects.create(
            letter_review=letter_review_obj, user=user
        )
        client.force_authenticate(user=different_user)
        url = f"/main_page/review_like{target_letter_review_like_obj.id}"
        response = client.delete(url)
        result = response.json()
        self.assertEqual(403, response.status_code)
        self.assertEqual("이 작업을 수행할 권한(permission)이 없습니다.", result["detail"])


class TestLetterReviewPostLikeUpdateGetAPI(APITestCase):
    """
    LetterisReadView API를 검증하는 클래스
    """

    def test_post_like_update_get(self) -> None:
        """
        lette_review_like post 의 data update get 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(
            username="hajin", password="1234", nickname="hajin"
        )
        daily_category = WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
            author_id=user.id, content="test", category_id=daily_cate.id
        )
        letter_obj = LetterModel.objects.create(
            letter_author=user,
            worryboard_id=worry_obj.id,
            title="test",
            content="test",
        )
        LetterReviewModel.objects.create(
            review_author=user,
            letter_id=letter_obj.id,
            content="test",
            grade=100,
        )

        test_order_grade_review_obj = LetterReviewModel.objects.order_by("-grade")[:1]

        letter_review_like_service(
            letter_review_id=test_order_grade_review_obj.get().id, user_id=user.id
        )

        test_user_create = UserModel.objects.create(username="test", nickname="test")
        test_worry_create = WorryBoardModel.objects.create(
            author_id=user.id, category_id=daily_category.id, content="test"
        )
        test_letter_create = LetterModel.objects.create(
            letter_author_id=test_user_create.id,
            worryboard_id=test_worry_create.id,
            title="test",
            content="test",
        )
        test_letter_review_create = LetterReviewModel.objects.create(
            review_author_id=user.id,
            letter_id=test_letter_create.id,
            content="test",
            grade=0,
        )

        client.force_authenticate(user=user)
        url = "/main_page/review/like_get"
        response = client.get(url)
        result = response.json()

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            result["live_review"][0]["review_id"], test_letter_review_create.id
        )
        self.assertEqual(
            result["best_review"][0]["grade"], test_order_grade_review_obj.get().grade
        )

    def test_when_user_is_unauthenticated_in_review_like_update_get(self) -> None:
        """
        Mainpage 의 get 함수를 검증하는 함수
        case : 인증되지 않은 유저일 때
        """
        client = APIClient()

        url = "/main_page/review/like_get"
        response = client.get(url)
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual(
            "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"]
        )
