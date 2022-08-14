# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from worry_board.models import RequestMessage

# from .webpush import webpush_request


# @receiver(post_save, sender=RequestMessage)
# def request_sended(sender, instance, created, **kwargs):

#     if created:
#         print("만들어짐!")
#         webpush_request(instance)
