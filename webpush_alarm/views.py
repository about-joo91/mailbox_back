from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from webpush import send_user_notification
from worry_board.models import RequestMessage, WorryBoard


class GetinfoView(APIView):
    def get(self, request):
        webpush_settings = getattr(settings, "WEBPUSH_SETTINGS", {})
        vapid_key = webpush_settings.get("VAPID_PUBLIC_KEY")
        user = request.user
        return Response({"vapid_key": vapid_key, "user": user.id}, status=status.HTTP_200_OK)


class SendWebpushView(APIView):
    def get(self, request):
        try:
            payload = {
                "head": "💌 편지 요청 확인 💌",
                "body": "아직 확인하지 않은 요청이 있습니다. 편지 받기 탭에서 내게 온 요청을 확인 해주세요!",
                "icon": "https://github.com/about-joo91/mailbox_front_dev/blob/main/images/mongle_with_letter.png?raw=true",  # 몽글이 이미지
            }
            user_worries = WorryBoard.objects.filter(author=request.user)
            undecided_worries = (
                RequestMessage.objects.filter(worry_board_id__in=user_worries.values_list("id", flat=True))
                .filter(request_status_id=2)
                .count()
            )

            if undecided_worries > 0:
                send_user_notification(user=request.user, payload=payload, ttl=2000)
            return Response(status=status.HTTP_200_OK)

        except TypeError:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
