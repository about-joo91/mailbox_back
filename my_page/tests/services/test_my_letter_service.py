from django.db.models import Q
from django.test import TestCase

from main_page.models import Letter as LetterModel
from main_page.models import WorryCategory as WorryCategoryModel
from main_page.services.letter_service import letter_post_service
from my_page.services.my_page_service import get_letter_data_by_user
from user.models import MongleGrade as MongleGradeModel
from user.models import MongleLevel as MongleLevelModel
from user.models import User as UserModel
from user.models import UserProfile as UserProfileModel
from worry_board.models import WorryBoard


class TestMyLetter(TestCase):
    """
    myletterservice를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):

        letter_author = UserModel.objects.create(username="letter_author", nickname="letter_author")
        UserProfileModel.objects.create(user=letter_author)
        mongle_level = MongleLevelModel.objects.create()
        MongleGradeModel.objects.create(user=letter_author, mongle_level=mongle_level)

        worry_author = UserModel.objects.create(username="worry_author", nickname="worry_author")
        UserProfileModel.objects.create(user=worry_author)
        MongleGradeModel.objects.create(user=worry_author, mongle_level=mongle_level)

        no_profile = UserModel.objects.create(username="no_profile", nickname="no_profile")
        MongleGradeModel.objects.create(user=no_profile, mongle_level=mongle_level)

        no_mongle_user = UserModel.objects.create(username="no_mongle", nickname="no_mongle")
        UserProfileModel.objects.create(user=no_mongle_user)

        WorryCategoryModel.objects.create(cate_name="1")

    def test_get_my_letter(self) -> None:
        """
        get_my_letter_service함수를 검증
        """
        # Given
        letter_author = UserModel.objects.get(username="letter_author")
        worry_board_author = UserModel.objects.get(username="worry_author")
        worry_category = WorryCategoryModel.objects.get(cate_name="1")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=worry_category,
        )
        LetterModel.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title="1",
            content="1",
        )

        # When
        with self.assertNumQueries(2):
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
        letter_author = UserModel.objects.get(username="no_profile")
        worry_board_author = UserModel.objects.get(username="worry_author")
        worry_category = WorryCategoryModel.objects.get(cate_name="1")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=worry_category,
        )
        LetterModel.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title=" ",
            content=" ",
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
        letter_author = UserModel.objects.get(username="no_mongle")
        worry_board_author = UserModel.objects.get(username="worry_author")
        worry_category = WorryCategoryModel.objects.get(cate_name="1")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=worry_category,
        )
        LetterModel.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title=" ",
            content=" ",
        )
        # When
        with self.assertRaises(UserModel.monglegrade.RelatedObjectDoesNotExist):
            query = Q(letter_author=letter_author)
            get_letter_data_by_user(query=query, letter_num=0)


class TestMyRecievedLetter(TestCase):
    """
    myrecievedletter를 검증하는 클래스
    """

    @classmethod
    def setUpTestData(cls):

        letter_author = UserModel.objects.create(username="letter_author", nickname="letter_author")
        UserProfileModel.objects.create(user=letter_author)
        mongle_level = MongleLevelModel.objects.create()
        MongleGradeModel.objects.create(user=letter_author, mongle_level=mongle_level)

        worry_author = UserModel.objects.create(username="worry_author", nickname="worry_author")
        UserProfileModel.objects.create(user=worry_author)
        MongleGradeModel.objects.create(user=worry_author, mongle_level=mongle_level)

        no_profile = UserModel.objects.create(username="no_profile", nickname="no_profile")
        MongleGradeModel.objects.create(user=no_profile, mongle_level=mongle_level)

        no_mongle_user = UserModel.objects.create(username="no_mongle", nickname="no_mongle")
        UserProfileModel.objects.create(user=no_mongle_user)

        WorryCategoryModel.objects.create(cate_name="1")

    def test_get_my_recieved_letter(self) -> None:
        """
        myrecievedletter함수를 검증
        """
        # Given
        letter_author = UserModel.objects.get(username="letter_author")
        worry_board_author = UserModel.objects.get(username="worry_author")
        worry_category = WorryCategoryModel.objects.get(cate_name="1")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=worry_category,
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
        with self.assertNumQueries(2):
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
        letter_author = UserModel.objects.get(username="no_profile")
        worry_board_author = UserModel.objects.get(username="worry_author")
        worry_category = WorryCategoryModel.objects.get(cate_name="1")
        worry_board = WorryBoard.objects.create(author=worry_board_author, category=worry_category)
        LetterModel.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title=" ",
            content=" ",
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
        letter_author = UserModel.objects.get(username="no_mongle")
        worry_board_author = UserModel.objects.get(username="worry_author")
        worry_category = WorryCategoryModel.objects.get(cate_name="1")
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=worry_category,
        )
        LetterModel.objects.create(
            letter_author=letter_author,
            worryboard=worry_board,
            title=" ",
            content=" ",
        )
        # When
        with self.assertRaises(UserModel.monglegrade.RelatedObjectDoesNotExist):
            query = Q(worryboard__author=worry_board_author)
            get_letter_data_by_user(query=query, letter_num=0)
