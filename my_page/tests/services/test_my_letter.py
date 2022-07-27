from django.db.models import Q
from django.test import TestCase

from main_page.models import Letter, WorryCategory
from my_page.services.my_page_service import get_letter_data_by_user
from user.models import User
from worry_board.models import WorryBoard


class TestMyLetter(TestCase):
    def test_get_my_ltter(self) -> None:
        # Given
        letter_author = User.objects.create(
            username="test", password="1234", nickname="1"
        )
        worry_board_author = User.objects.create(
            username="test1", password="1234", nickname="2"
        )
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=WorryCategory.objects.create(cate_name="1"),
        )
        Letter.objects.create(
            letter_author=letter_author, worryboard=worry_board, title="1"
        )

        # When
        with self.assertNumQueries(1):
            query = Q(letter_author=letter_author)
            test_letter_this_page = get_letter_data_by_user(query=query, letter_num=0)
            # Then
            self.assertEqual("1", test_letter_this_page["category"])
            self.assertEqual("1", test_letter_this_page["title"])
            self.assertEqual("", test_letter_this_page["content"])

    def test_my_recieved_letter_get(self) -> None:
        # Given
        letter_author = User.objects.create(
            username="test", password="1234", nickname="1"
        )
        worry_board_author = User.objects.create(
            username="test1", password="1234", nickname="2"
        )
        worry_board = WorryBoard.objects.create(
            author=worry_board_author,
            category=WorryCategory.objects.create(cate_name="1"),
        )
        Letter.objects.create(letter_author=letter_author, worryboard=worry_board)
        worry_board2 = WorryBoard.objects.create(
            author=worry_board_author,
            category=WorryCategory.objects.create(cate_name="1"),
        )
        Letter.objects.create(
            letter_author=letter_author, worryboard=worry_board2, title="1"
        )

        # When
        with self.assertNumQueries(1):
            query = Q(worryboard__author=worry_board_author)
            test_letter_this_page = get_letter_data_by_user(query=query, letter_num=1)

            # Then
            self.assertEqual("1", test_letter_this_page["category"])
            self.assertEqual("1", test_letter_this_page["title"])
            self.assertEqual("", test_letter_this_page["content"])
