from django.contrib import admin

from .models import RequestMessage as RequestMessageModel
from .models import RequestStatus as RequestStatusModel

# Register your models here.


admin.site.register(RequestMessageModel)
admin.site.register(RequestStatusModel)
