import json

from rest_framework.test import APIClient, APITestCase

from user.models import Report
from user.models import User as UserModel
from user.services.report_service import create_user_report


class ReportUserView(APITestCase):
    """
    ReportUserView를 검증하는 클래스
    """

    def test_report_post(self):
        """
        ReportUserView의 포스트를 검증하는 함수
        """
        client = APIClient()
        user = UserModel.objects.create(username="test", nickname="test")
        target_user = UserModel.objects.create(username="reported_user", nickname="reported_user")
        report_reason = "욕했어요!"

        client.force_authenticate(user=user)
        url = "/user/report"
        response = client.post(
            url,
            json.dumps({"target_user_id": target_user.id, "report_reason": report_reason}),
            content_type="application/json",
        )
        result = response.json()

        report_model_cnt = Report.objects.all().count()
        report_model = Report.objects.filter(report_user_id=user.id, reported_user__user_id=target_user.id).get()

        self.assertEqual(200, response.status_code)
        self.assertEqual(f"{target_user.username}유저를 신고하셨습니다.", result["detail"])
        self.assertEqual(1, report_model_cnt)
        self.assertEqual(report_reason, report_model.report_reason)

    def test_when_report_is_already_exist_in_report_post(self):
        """
        ReportUserView의 포스트를 검증하는 함수
        case:유저가 이미 신고를 했을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="test", nickname="test")
        target_user = UserModel.objects.create(username="reported_user", nickname="reported_user")
        report_reason = "욕했어요!"
        create_user_report(user_id=user.id, target_user_id=target_user.id, report_reason=report_reason)

        client.force_authenticate(user=user)
        url = "/user/report"
        response = client.post(
            url,
            json.dumps({"target_user_id": target_user.id, "report_reason": report_reason}),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("이미 신고하셨습니다.", result["detail"])

    def test_when_target_user_does_not_exist_in_report_post(self):
        """
        ReportUserView의 포스트를 검증하는 함수
        case:대상유저가 없을 때
        """
        client = APIClient()
        user = UserModel.objects.create(username="test", nickname="test")
        report_reason = "욕했어요!"

        client.force_authenticate(user=user)
        url = "/user/report"
        response = client.post(
            url,
            json.dumps({"target_user_id": 999, "report_reason": report_reason}),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(404, response.status_code)
        self.assertEqual("999는 없는 유저입니다.", result["detail"])

    def test_when_user_is_unauthenticated_in_report_post(self):
        """
        ReportUserView의 포스트를 검증하는 함수
        case:인증되지 않은 유저일 때
        """
        client = APIClient()
        target_user = UserModel.objects.create(username="reported_user", nickname="reported_user")
        report_reason = "욕했어요!"

        url = "/user/report"
        response = client.post(
            url,
            json.dumps({"target_user_id": target_user.id, "report_reason": report_reason}),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(401, response.status_code)
        self.assertEqual("자격 인증데이터(authentication credentials)가 제공되지 않았습니다.", result["detail"])
