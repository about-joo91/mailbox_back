import json

from rest_framework.test import APIClient, APITestCase

from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from main_page.models import WorryCategory as WorryCategoryModel
from main_page.models import Letter as LetterModel
from worry_board.models import WorryBoard as WorryBoardModel
from main_page.services.letter_service import letter_post_service


class TestLetterviewAPI(APITestCase):
    """
    Lettervie 의 API를 검증하는 클래스
    """
    def test_letter_post(self) -> None:
        """
        LetterReviewLike 의 post 함수를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(username="hajin", password="1234", nickname="hajin")
        user_profile_info ={
            "user" : user,
            "mongle_grade" : 100
        }
        UserProfileModel.objects.create(**user_profile_info)
        
        WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
                    author_id=user.id, content="test", category_id=daily_cate.id
                )

        client.force_authenticate(user=user)
        url = "/main_page/letter/"
        letter_title = "테스트 입니다!"
        letter_content = "테스트 입니다!"
        response = client.post(
            url,
            json.dumps(
                {
                    "worry_board_id": worry_obj.id,
                    "title" : letter_title,
                    "content" : letter_content
                    
                    }
                    ),
            content_type="application/json",
            )
        result = response.json()

        test_letter_obj =LetterModel.objects.order_by("-create_date")[:1].get().letter_author.id

        self.assertEqual(200, response.status_code)
        self.assertEqual(user.id, test_letter_obj)
        self.assertEqual(result["detail"], "편지 작성이 완료 되었습니다.")



    def test_inappropriate_content_letter_post(self) -> None:
        """
        LetterReviewLike 의 post 함수를 검증하는 함수
        case:  부적절한 내용이 담겨있을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="hajin", password="1234", nickname="hajin")
        user_profile_info ={
            "user" : user,
            "mongle_grade" : 100
        }
        UserProfileModel.objects.create(**user_profile_info)
        
        WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
                    author_id=user.id, content="test", category_id=daily_cate.id
                )

        client.force_authenticate(user=user)
        url = "/main_page/letter/"
        letter_title = "테스트 입니다!"
        letter_content = "시발시발시발시발"
        response = client.post(
            url,
            json.dumps(
                {
                    "worry_board_id": worry_obj.id,
                    "title" : letter_title,
                    "content" : letter_content
                    
                    }
                    ),
            content_type="application/json",
            )
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(result["detail"], "부적절한 내용이 담겨있어 게시글을 올릴 수 없습니다")


    def test_overlap_letter_post(self) -> None:
        """
        LetterReviewLike 의 post 함수를 검증하는 함수
        case: 이미 편지를 작성했을 경우
        """
        client = APIClient()
        user = UserModel.objects.create(username="hajin", password="1234", nickname="hajin")
        user_profile_info ={
            "user" : user,
            "mongle_grade" : 100
        }
        UserProfileModel.objects.create(**user_profile_info)
        
        WorryCategoryModel.objects.create(cate_name="일상")
        daily_cate = WorryCategoryModel.objects.get(cate_name="일상")
        worry_obj = WorryBoardModel.objects.create(
                    author_id=user.id, content="test", category_id=daily_cate.id
                )
        LetterModel.objects.create(letter_author_id=user.id,worryboard_id=worry_obj.id,title="test",content="content")

        client.force_authenticate(user=user)
        url = "/main_page/letter/"
        letter_title = "테스트 입니다!"
        letter_content = "테스트 입니다!"
        response = client.post(
            url,
            json.dumps(
                {
                    "worry_board_id": worry_obj.id,
                    "title" : letter_title,
                    "content" : letter_content
                    
                    }
                    ),
            content_type="application/json",
            )
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(result["detail"], "이미 편지를 작성 하셨습니다.")