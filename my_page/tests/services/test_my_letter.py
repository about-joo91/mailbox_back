from django.db.models import Q
from django.test import TestCase

from main_page.models import WorryCategory as WorryCategoryModel
from main_page.services.letter_service import letter_post_service
from my_page.services.my_page_service import get_letter_data_by_user
from user.models import MongleGrade as MongleGradeModel
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from user.services.user_signup_login_service import post_user_signup_data
from worry_board.models import WorryBoard


class TestMyLetter(TestCase):
    """
    myletterservice를 검증하는 클래스
    """

    def test_get_my_letter(self) -> None:
        """
        get_my_letter_service함수를 검증
        """
        # Given
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worryboard_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = UserModel.objects.get(username="test_letter_author")
        worry_board_author = UserModel.objects.get(username="test_worryboard_author")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=WorryCategoryModel.objects.create(cate_name="1"),
        )
        letter_post_service(
            letter_author=letter_author,
            request_data={
                "worry_board_id": worry_board.id,
                "title": "1",
                "content": "1",
            },
        )

        # When
        with self.assertNumQueries(1):
            query = Q(letter_author=letter_author)
            test_letter_this_page = get_letter_data_by_user(query=query, letter_num=0)
            # Then
            self.assertEqual("1", test_letter_this_page["category"])
            self.assertEqual("1", test_letter_this_page["title"])
            self.assertEqual("1", test_letter_this_page["content"])

    def test_when_user_profile_is_none_get_my_letter(self) -> None:
        """
        get_my_letter_service함수를 검증
        case: userprofile이 none일 때
        """
        # Given
        letter_author = UserModel.objects.create(
            username="letter_author", nickname="letter_author"
        )
        MongleGradeModel.objects.create(user=letter_author)
        worry_board_author = UserModel.objects.create(
            username="worryboard_author", nickname="worryboard_author"
        )
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=WorryCategoryModel.objects.create(cate_name="1"),
        )
        MongleGradeModel.objects.create(user=worry_board_author)
        letter_post_service(
            letter_author=letter_author,
            request_data={
                "worry_board_id": worry_board.id,
                "title": "1",
                "content": "1",
            },
        )

        # When
        with self.assertRaises(UserModel.userprofile.RelatedObjectDoesNotExist):
            query = Q(letter_author=letter_author)
            get_letter_data_by_user(query=query, letter_num=0)

    def test_when_mongle_is_none_get_my_letter(self) -> None:
        """
        get_my_letter_service함수를 검증
        case: monglegrade가 none일 때
        """
        # Given
        letter_author = UserModel.objects.create(
            username="letter_author", nickname="letter_author"
        )
        UserProfileModel.objects.create(user=letter_author)
        worry_board_author = UserModel.objects.create(
            username="worryboard_author", nickname="worryboard_author"
        )
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=WorryCategoryModel.objects.create(cate_name="1"),
        )
        UserProfileModel.objects.create(user=worry_board_author)
        letter_post_service(
            letter_author=letter_author,
            request_data={
                "worry_board_id": worry_board.id,
                "title": "1",
                "content": "1",
            },
        )

        # When
        with self.assertRaises(UserModel.monglegrade.RelatedObjectDoesNotExist):
            query = Q(letter_author=letter_author)
            get_letter_data_by_user(query=query, letter_num=0)


class TestMyRecievedLetter(TestCase):
    """
    myrecievedletter를 검증하는 클래스
    """

    def test_get_my_recieved_letter(self) -> None:
        """
        myrecievedletter함수를 검증
        """
        # Given
        post_user_signup_data(
            user_data={
                "username": "test_letter_author",
                "password": "123456qwe@",
                "nickname": "1",
            }
        )
        post_user_signup_data(
            user_data={
                "username": "test_worryboard_author",
                "password": "123456qwe@",
                "nickname": "2",
            }
        )
        letter_author = UserModel.objects.get(username="test_letter_author")
        worry_board_author = UserModel.objects.get(username="test_worryboard_author")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=WorryCategoryModel.objects.create(cate_name="1"),
        )
        letter_post_service(
            letter_author=letter_author,
            request_data={
                "worry_board_id": worry_board.id,
                "title": "2",
                "content": "3",
            },
        )

        # When
        with self.assertNumQueries(1):
            query = Q(worryboard__author=worry_board_author)
            test_letter_this_page = get_letter_data_by_user(query=query, letter_num=0)

            # Then
            self.assertEqual("1", test_letter_this_page["category"])
            self.assertEqual("2", test_letter_this_page["title"])
            self.assertEqual("3", test_letter_this_page["content"])

    def test_when_user_profile_is_none_get_my_letter(self) -> None:
        """
        myrecievedletter함수를 검증
        case: userprofile이 none일 때
        """
        # Given
        letter_author = UserModel.objects.create(
            username="letter_author", nickname="letter_author"
        )
        MongleGradeModel.objects.create(user=letter_author)
        worry_board_author = UserModel.objects.create(
            username="worryboard_author", nickname="worryboard_author"
        )
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=WorryCategoryModel.objects.create(cate_name="1"),
        )
        MongleGradeModel.objects.create(user=worry_board_author)
        letter_post_service(
            letter_author=letter_author,
            request_data={
                "worry_board_id": worry_board.id,
                "title": "1",
                "content": "1",
            },
        )

        # When

        with self.assertRaises(UserModel.userprofile.RelatedObjectDoesNotExist):
            query = Q(worryboard__author=worry_board_author)
            get_letter_data_by_user(query=query, letter_num=0)

    def test_when_mongle_is_none_get_my_letter(self) -> None:
        """
        myrecievedletter함수를 검증
        case: monglegrade가 none일 때
        """
        # Given
        letter_author = UserModel.objects.create(
            username="letter_author", nickname="letter_author"
        )
        UserProfileModel.objects.create(user=letter_author)
        worry_board_author = UserModel.objects.create(
            username="worryboard_author", nickname="worryboard_author"
        )
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=WorryCategoryModel.objects.create(cate_name="1"),
        )
        UserProfileModel.objects.create(user=worry_board_author)
        letter_post_service(
            letter_author=letter_author,
            request_data={
                "worry_board_id": worry_board.id,
                "title": "1",
                "content": "1",
            },
        )

        # When
        with self.assertRaises(UserModel.monglegrade.RelatedObjectDoesNotExist):
            query = Q(worryboard__author=worry_board_author)
            get_letter_data_by_user(query=query, letter_num=0)
