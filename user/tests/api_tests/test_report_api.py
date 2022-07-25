import json

from rest_framework.test import APIClient, APITestCase

from user.models import Report
from user.models import User as UserModel
from user.services.report_service import create_user_report


class ReportUserView(APITestCase):
    def test_report_post(self):

        client = APIClient()
        user = UserModel.objects.create(username="test", nickname="test")
        target_user = UserModel.objects.create(
            username="reported_user", nickname="reported_user"
        )
        report_reason = "욕했어요!"

        client.force_authenticate(user=user)
        url = "/user/report"
        response = client.post(
            url,
            json.dumps(
                {"target_user_id": target_user.id, "report_reason": report_reason}
            ),
            content_type="application/json",
        )
        result = response.json()

        report_model_cnt = Report.objects.all().count()
        report_model = Report.objects.filter(
            report_user_id=user.id, reported_user__user_id=target_user.id
        ).get()

        self.assertEqual(200, response.status_code)
        self.assertEqual(f"{target_user.username}유저를 신고하셨습니다.", result["detail"])
        self.assertEqual(1, report_model_cnt)
        self.assertEqual(report_reason, report_model.report_reason)

    def test_when_report_is_already_exist_report_post(self):

        client = APIClient()
        user = UserModel.objects.create(username="test", nickname="test")
        target_user = UserModel.objects.create(
            username="reported_user", nickname="reported_user"
        )
        report_reason = "욕했어요!"
        create_user_report(
            user_id=user.id, target_user_id=target_user.id, report_reason=report_reason
        )

        client.force_authenticate(user=user)
        url = "/user/report"
        response = client.post(
            url,
            json.dumps({"target_user_id": target_user.id, "report_reason": "사실 욕 안함"}),
            content_type="application/json",
        )
        result = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual("이미 신고하셨습니다.", result["detail"])
