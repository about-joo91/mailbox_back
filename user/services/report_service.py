from django.db.models import Count

from user.models import Report
from user.models import Report as ReportModel
from user.models import ReportedUser
from user.models import ReportedUser as ReportedUserModel

REPORT_CONDITION_CNT = 3


def create_user_report(user_id: int, target_user_id: int, report_reason: str) -> str:
    """
    유저를 신고하는 service
    """
    target_user, _ = ReportedUserModel.objects.get_or_create(user_id=target_user_id)
    ReportModel.objects.create(
        report_user_id=user_id, report_reason=report_reason, reported_user=target_user
    )
    return target_user.user.username


def get_reported_user_over_condition_cnt() -> None:
    """
    condition 이상으로 신고된 유저를 찾고 그 유저의 active값을 변경하는 함수
    """
    report_cnt_over_condition_reported_users = list(
        ReportedUser.objects.select_related("user")
        .annotate(reported_cnt=Count("report"))
        .filter(reported_cnt__gte=REPORT_CONDITION_CNT)
    )

    for reported_user in report_cnt_over_condition_reported_users:
        reported_user.user.is_active = False
        reported_user.user.save()

    Report.objects.all().delete()
