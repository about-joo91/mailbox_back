from django.contrib import admin

from .models import Report as ReportModel
from .models import ReportedUser as ReportedUserModel
from .models import User as UserModel
from .models import UserProfile as UserProfileModel

# Register your models here.
admin.site.register(UserModel)
admin.site.register(UserProfileModel)
admin.site.register(ReportModel)
admin.site.register(ReportedUserModel)
