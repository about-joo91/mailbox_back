from django.contrib import admin
from .models import (
    User as UserModel,
    UserProfile as UserProfileModel,
    Report as ReportModel,
    ReportedUser as ReportedUserModel,
    )

# Register your models here.
admin.site.register(UserModel)
admin.site.register(UserProfileModel)
admin.site.register(ReportModel)
admin.site.register(ReportedUserModel)
