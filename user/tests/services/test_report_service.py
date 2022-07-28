from django.db import IntegrityError
from django.test import TestCase

from user.models import Report
from user.models import User as UserModel
from user.services.report_service import (
    create_user_report,
    get_reported_user_over_condition,
)


class TestUserReportService(TestCase):
    """
    condition 이상으로 신고된 유저를 찾고 그 유저의 active값을 변경하는 함수를 검증
    """

    def test_get_reported_user_over_condition(self):
        """
        report_condition에 맞게 데이터가 나오는지 검증
        """
        user1 = UserModel.objects.create(
            username="report_test1", nickname="report_test1"
        )
        user2 = UserModel.objects.create(
            username="report_test2", nickname="report_test2"
        )
        user3 = UserModel.objects.create(
            username="report_test3", nickname="report_test3"
        )
        report_users = [user1, user2, user3]
        reported_user = UserModel.objects.create(
            username="report_test4", nickname="report_test4"
        )
        for user in report_users:
            user_id = user.id
            create_user_report(
                user_id=user_id, target_user_id=reported_user.id, report_reason=" "
            )

        self.assertEqual(3, Report.objects.all().count())

        with self.assertNumQueries(3):
            get_reported_user_over_condition()

        reported_user = UserModel.objects.filter(id=reported_user.id).get()

        self.assertEqual(0, Report.objects.all().count())
        self.assertEqual(False, reported_user.is_active)

    def test_create_user_report(self):
        """
        유저를 신고하는 함수를 검증
        """
        user = UserModel.objects.create(username="report_test", nickname="report_test")
        reported_user = UserModel.objects.create(
            username="reported_test", nickname="reported_test"
        )
        report_reason = "편지에 욕설을 적었습니다."
        reported_user_name = create_user_report(
            user_id=user.id,
            target_user_id=reported_user.id,
            report_reason=report_reason,
        )

        this_report_object = Report.objects.filter(report_user=user).get()
        self.assertEqual(1, Report.objects.all().count())
        self.assertEqual("reported_test", reported_user_name)
        self.assertEqual(report_reason, this_report_object.report_reason)

    def test_when_reported_user_is_none_in_create_user_report(self):
        """
        유저를 신고하는 함수를 검증
        case:신고대상 유저가 없을 때
        """
        user = UserModel.objects.create(username="test", nickname="test")
        report_reason = "편지에 욕설을 적었습니다."
        with self.assertRaises(UserModel.DoesNotExist):
            create_user_report(
                user_id=user.id, target_user_id=999, report_reason=report_reason
            )

    def test_when_user_report_multiple_time_same_user_in_create_user_report(self):
        """
        유저를 신고하는 함수를 검증
        case: 유저가 중복신고를 했을 때
        """
        user = UserModel.objects.create(username="report_test", nickname="report_test")
        reported_user = UserModel.objects.create(
            username="reported_test", nickname="reported_test"
        )
        report_reason = "편지에 욕설을 적었습니다."

        with self.assertRaises(IntegrityError):
            for _ in range(2):
                create_user_report(
                    user_id=user.id,
                    target_user_id=reported_user.id,
                    report_reason=report_reason,
                )
