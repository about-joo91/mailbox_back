from django.test import TestCase
from main_page.services.main_gage_service import recommend_worryboard_list

from user.models import User as UserModel
from worry_board.models import WorryBoard as WorryBoardModel
from main_page.models import WorryCategory as WorryCategoryModel
from main_page.models import Letter as LetterModel

class TestRecommendationService(TestCase):
    """
    추천시스템 service를 검증 
    """

    def test_recommend_worryboard_list(self):
        """
        추천시스템 
        """
        user = UserModel.objects.create(username="won1", password="1234", nickname="won")
        user_2 = UserModel.objects.create(username="won2", password="1234", nickname="won2")
        user_3 = UserModel.objects.create(username="won3", password="1234", nickname="won3")
        
        category_list = ["일상", "연애", "학업", "가족", "인간관계", "육아"]
        for cate_name in category_list:
            WorryCategoryModel.objects.create(cate_name=cate_name)

        first_cate = WorryCategoryModel.objects.get(cate_name="일상").id
        second_cate = WorryCategoryModel.objects.get(cate_name="연애").id
        last_cate = WorryCategoryModel.objects.get(cate_name="육아").id

        worry_obj1 = WorryBoardModel.objects.create(author=user, content="너무 더운데 뭘 먹을까요", category_id=first_cate)
        worry_obj2 = WorryBoardModel.objects.create(author=user_2, content="사랑이 뭔가요", category_id=second_cate)
        worry_obj3 = WorryBoardModel.objects.create(author=user_2, content="연애를 하고 싶어요", category_id=second_cate)
        worry_obj4 = WorryBoardModel.objects.create(author=user_3, content="사랑할 수 있을까요", category_id=second_cate)
        worry_obj5 = WorryBoardModel.objects.create(author=user_3, content="아이가 밤마다 울어요ㅠㅠ", category_id=last_cate)

        LetterModel.objects.create(
            letter_author_id=user.id,
            worryboard_id=worry_obj2.id,
            title="title",
            content="test",
        )
        
        recommend_worryboard_list(user)
        
        
        
    def test_recommend_worryboard_list(self):
        """
        추천시스템 
        """
