from django.contrib import admin
from .models import (
    User as UserModel,
    Report as ReportModel,
    UserProfile as UserProfileModel,
    )

# Register your models here.
admin.site.register(UserModel)
admin.site.register(ReportModel)
admin.site.register(UserProfileModel)
