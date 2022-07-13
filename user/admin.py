from django.contrib import admin
from .models import (
    User as UserModel,
    UserProfile as UserProfileModel,
    ReportUser as ReportUserModel,
    ReportedUser as ReportedUserModel,
    )

# Register your models here.
admin.site.register(UserModel)
admin.site.register(UserProfileModel)
admin.site.register(ReportUserModel)
admin.site.register(ReportedUserModel)
