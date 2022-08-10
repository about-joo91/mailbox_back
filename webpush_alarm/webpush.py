# import json

from webpush import send_user_notification

# from worry_board.models import RequestMessage


def webpush_request(instance):
    print("webpush 함수로 들어왔다!")
    print(instance)

    user = instance.worry_board.author
    print(user)

    payload = {
        "head": "띵동~",
        "body": "고민에 대해 편지 요청이 들어왔어요!",
        "icon": "https://i.imgur.com/dRDxiCQ.png",  # 몽글이 이미지 링크를 넣자
        "url": "https://www.naver.com",
    }  # 내가받은 요청 페이지로 가자
    print(payload)
    # payload = json.dumps(payload)
    # print(payload)

    send_user_notification(user=user, payload=payload, ttl=1000)
