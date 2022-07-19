from django.test import TestCase

from jin.models import Letter, WorryCategory
from my_page.serializers import LetterSerializer
from user.models import User
from worry_board.models import WorryBoard


class TestMyLetter(TestCase):
    def test_my_ltter_get(self) -> None:
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
        Letter.objects.create(letter_author=letter_author, worryboard=worry_board2)

        # When
        with self.assertNumQueries(2):
            test_letter_cnt = Letter.objects.filter(letter_author=letter_author).count()
            test_letter_this_page = Letter.objects.select_related(
                "worryboard__category"
            ).filter(letter_author=letter_author)[0]
            # test_letter_this_page = Letter.objects.filter(letter_author = letter_author).annotate(letter_cnt=Count('id'))
            letter_data = LetterSerializer(test_letter_this_page).data
            # Then
            self.assertEqual(2, test_letter_cnt)
            self.assertEqual("1", letter_data["category"])
