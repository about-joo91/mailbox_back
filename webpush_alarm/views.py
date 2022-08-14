import json

from django.conf import settings
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404

# from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from rest_framework_simplejwt.authentication import JWTAuthentication
from webpush import send_user_notification
from webpush.utils import send_notification_to_user

from user.models import User
from worry_board.models import RequestMessage, WorryBoard

# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_GET, require_POST


class CheckLoginView(APIView):
    def get(self, request):
        # user = User.objects.get(id = request.user.id)
        # user.is_login = "True"
        # user.save()

        webpush = webpush_request(request.user)
        print(webpush)
        return Response({"message": webpush})


def webpush_request(user_obj):
    print("webpush 함수로 들어왔다!")

    undecided_worries = 0
    user_worries = WorryBoard.objects.filter(author=user_obj)
    for worry in user_worries:
        requests = RequestMessage.objects.filter(worry_board_id=worry.id).exclude(request_status_id=2).count()
        if requests == 0:
            undecided_worries += 1
    print(undecided_worries)

    if undecided_worries > 0:

        payload = {
            "head": "띵동~",
            "body": "확인하지 않은 요청이 존재합니다",
            "icon": "https://i.imgur.com/dRDxiCQ.png",  # 몽글이 이미지 링크를 넣자
            "url": "https://www.naver.com",  # 내가받은 요청 페이지로 가자
        }

        send_user_notification(user=user_obj, payload=payload, ttl=1000)
        payload = json.dumps(payload)
        return payload
    return "요청이 없습니다"


############################################


class WebpushView(APIView):
    def get(self, request):
        print("home get")
        webpush_settings = getattr(settings, "WEBPUSH_SETTINGS", {})
        print(webpush_settings)
        vapid_key = webpush_settings.get("VAPID_PUBLIC_KEY")
        print(vapid_key)
        user = request.user
        print(user)
        return Response({"vapid_key": vapid_key, "user": user.id}, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            body = request.body
            data = json.loads(body)
            print(data)

            if "head" not in data or "body" not in data or "id" not in data:
                return JsonResponse(status=400, data={"message": "Invalid data format"})

            user_id = data["id"]
            print(user_id)
            user = get_object_or_404(User, pk=user_id)
            payload = {"head": data["head"], "body": data["body"]}
            payload = json.dumps(payload)
            send_notification_to_user(user=user, payload=payload, ttl=100000)
            print("여기까지 들어옴!!")

            return JsonResponse(status=200, data={"message": "Web push successful"})
        except TypeError:
            return JsonResponse(status=500, data={"message": "An error occurred"})
